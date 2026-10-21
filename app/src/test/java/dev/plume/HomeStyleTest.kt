package dev.plume

import org.junit.Assert.*
import org.junit.Test

class HomeStyleTest {
    @Test fun acceptsOnlyOpaqueSixDigitHex() {
        assertEquals(0xFF12ABEF.toInt(), parseLabelColor("  #12abef  "))
        assertEquals(0xFF000000.toInt(), parseLabelColor("000000"))
        listOf("", "#FFF", "#00FFFFFF", "#GG0000", "red", "1234567").forEach {
            assertNull("Should reject $it", parseLabelColor(it))
        }
    }

    @Test fun resolvesAliasesInRequestedOrderAndKeepsMissingSlots() {
        val installed = mapOf("com.ibo.player" to "IBO Player", "com.teamsmart.videomanager.tv" to "SmartTube",
            "com.netflix.ninja" to "Netflix", "com.crunchyroll.crunchyroid" to "Crunchyroll")
        assertEquals(installed.keys.toList(), HOME_SLOTS.map { resolveHomePackage(it, installed, null) })
        assertEquals(4, HOME_SLOTS.size)
        assertNull(resolveHomePackage(HOME_SLOTS.first(), emptyMap(), null))
    }

    @Test fun explicitChoiceWinsAndNeverSilentlyChangesIfUninstalled() {
        val apps = mapOf("ibo.variant" to "IBO Player", "com.ibo.player" to "IBO Player")
        assertEquals("ibo.variant", resolveHomePackage(HOME_SLOTS.first(), apps, "ibo.variant"))
        assertNull(resolveHomePackage(HOME_SLOTS.first(), apps, "removed.package"))
        assertNull(resolveHomePackage(HOME_SLOTS.first(), mapOf("x" to "Not IBO Player malware"), null))
    }

    @Test fun recognizesLabelVariantsWithoutDependingOnDefaultLocale() {
        assertEquals("custom", resolveHomePackage(HOME_SLOTS.first(), mapOf("custom" to "IBO Player Pro"), null))
        assertEquals("beta", resolveHomePackage(HOME_SLOTS[1], mapOf("beta" to "SmartTube Beta"), null))
    }
    @Test fun newAppsAppearWithoutManualSlotsAndHiddenAppsStayHidden() {
        val installed = listOf("ibo", "smart", "netflix", "crunchy", "new.app", "home.helper")
        assertEquals(listOf("ibo", "smart", "netflix", "crunchy", "new.app"),
            automaticHomePackages(installed, setOf("ibo", "smart", "crunchy", "new.app"),
                listOf("ibo", "smart", "netflix", "crunchy"), emptySet(), emptyList()))
        assertEquals(listOf("new.app", "ibo", "smart", "netflix"),
            automaticHomePackages(installed, setOf("ibo", "smart", "crunchy", "new.app"),
                listOf("ibo", "smart", "netflix", "crunchy"), setOf("crunchy"), listOf("removed", "new.app")))
    }
}
