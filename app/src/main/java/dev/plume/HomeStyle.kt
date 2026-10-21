package dev.plume

import java.util.Locale

internal data class HomeSlot(val id: String, val title: String, val packages: List<String>, val labels: Set<String>)

internal val HOME_SLOTS = listOf(
    HomeSlot("ibo", "IBO Player", listOf("com.ibo.player", "com.iboplayer", "com.ibopro.player", "com.flextv.livestore"),
        setOf("ibo player", "iboplayer", "ibo player pro", "ibo player officiel")),
    HomeSlot("smarttube", "SmartTube", listOf("org.smarttube.stable", "org.smarttube.beta", "com.teamsmart.videomanager.tv", "com.liskovsoft.smarttubetv.beta"),
        setOf("smarttube", "smarttube beta", "smarttube next", "smarttubenext")),
    HomeSlot("netflix", "Netflix", listOf("com.netflix.ninja", "com.netflix.mediaclient"), setOf("netflix")),
    HomeSlot("crunchyroll", "Crunchyroll", listOf("com.crunchyroll.crunchyroid", "com.crunchyroll.crunchyroid.tv"), setOf("crunchyroll")),
)

/** Strictly opaque RGB: an alpha typo must never make all the app names disappear. */
internal fun parseLabelColor(raw: String): Int? {
    val hex = raw.trim().removePrefix("#")
    if (!hex.matches(Regex("[0-9a-fA-F]{6}"))) return null
    return (0xFF000000L or hex.toLong(16)).toInt()
}

/** A saved choice is authoritative; do not launch a different app if it has been uninstalled. */
internal fun resolveHomePackage(slot: HomeSlot, installed: Map<String, String>, chosen: String?): String? {
    if (chosen != null) return chosen.takeIf { it in installed }
    return slot.packages.firstOrNull { it in installed }
        ?: installed.entries.firstOrNull { it.value.trim().lowercase(Locale.ROOT) in slot.labels }?.key
}

/** New user apps join automatically; existing hidden apps and a manual order survive package changes. */
internal fun automaticHomePackages(installed: List<String>, userApps: Set<String>, preferred: List<String>,
    hidden: Set<String>, savedOrder: List<String>): List<String> {
    val eligible = (preferred + installed.filter { it in userApps }).distinct()
        .filter { it in installed && it !in hidden }
    return eligible.sortedWith(compareBy<String> { savedOrder.indexOf(it).let { n -> if (n < 0) Int.MAX_VALUE else n } })
}
