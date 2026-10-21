package dev.plume

import android.content.res.Resources
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.Rect
import android.graphics.drawable.AdaptiveIconDrawable
import android.graphics.drawable.BitmapDrawable
import android.graphics.drawable.Drawable
import android.graphics.drawable.LayerDrawable

/** Uses only the installed icon. Trim transparent padding and extend its own edge colour. */
internal fun appArtwork(icon: Drawable, resources: Resources): Drawable {
    val original = (icon.constantState?.newDrawable(resources) ?: icon).mutate()
    val layers = if (original is AdaptiveIconDrawable)
        LayerDrawable(arrayOf(original.background, original.foreground)) else original
    val size = 192
    val bitmap = Bitmap.createBitmap(size, size, Bitmap.Config.ARGB_8888)
    layers.setBounds(0, 0, size, size)
    layers.draw(Canvas(bitmap))
    val pixels = IntArray(size * size)
    bitmap.getPixels(pixels, 0, size, 0, 0, size, size)
    var left = size; var top = size; var right = 0; var bottom = 0
    for (y in 0 until size) for (x in 0 until size) {
        if (pixels[y * size + x] ushr 24 > 220) {
            left = minOf(left, x); top = minOf(top, y)
            right = maxOf(right, x); bottom = maxOf(bottom, y)
        }
    }
    if (left > right || top > bottom) { bitmap.recycle(); return original }
    val counts = HashMap<Int, Int>()
    val colours = HashMap<Int, Int>()
    fun sample(x: Int, y: Int) {
        val c = pixels[y * size + x]
        if (c ushr 24 <= 220) return
        val bucket = c and 0x00F8F8F8
        counts[bucket] = (counts[bucket] ?: 0) + 1
        colours[bucket] = c or 0xFF000000.toInt()
    }
    val insetX = (right - left) / 12; val insetY = (bottom - top) / 12
    for (x in left..right) { sample(x, top + insetY); sample(x, bottom - insetY) }
    for (y in top..bottom) { sample(left + insetX, y); sample(right - insetX, y) }
    val background = counts.maxByOrNull { it.value }?.key?.let { colours[it] } ?: 0xFF202024.toInt()
    val height = size * 10 / 16
    val output = Bitmap.createBitmap(size, height, Bitmap.Config.ARGB_8888)
    Canvas(output).apply {
        drawColor(background)
        // Keep every letter and the whole logo; extend its native colour across the rectangle.
        val w = right - left + 1; val h = bottom - top + 1
        val scale = minOf(size.toFloat() / w, height.toFloat() / h)
        val dw = (w * scale).toInt().coerceAtLeast(1)
        val dh = (h * scale).toInt().coerceAtLeast(1)
        val x = (size - dw) / 2; val y = (height - dh) / 2
        drawBitmap(bitmap, Rect(left, top, right + 1, bottom + 1), Rect(x, y, x + dw, y + dh), Paint(Paint.FILTER_BITMAP_FLAG))
    }
    bitmap.recycle()
    return BitmapDrawable(resources, output)
}
