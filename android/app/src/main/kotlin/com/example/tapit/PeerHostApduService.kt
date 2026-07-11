package com.example.tapit

import android.nfc.cardemulation.HostApduService
import android.os.Bundle
import java.nio.charset.StandardCharsets

class PeerHostApduService : HostApduService() {
    override fun processCommandApdu(commandApdu: ByteArray, extras: Bundle?): ByteArray {
        if (isSelectApdu(commandApdu)) {
            return SUCCESS_SW
        }

        if (isGetDataApdu(commandApdu)) {
            val payload = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
                .getString(PREF_KEY_PAYLOAD, defaultPayload())
                ?: defaultPayload()

            return payload.toByteArray(StandardCharsets.UTF_8) + SUCCESS_SW
        }

        return UNKNOWN_COMMAND_SW
    }

    override fun onDeactivated(reason: Int) {
        // No-op. The payload is stored in shared preferences so it stays available.
    }

    private fun isSelectApdu(commandApdu: ByteArray): Boolean {
        return commandApdu.size >= 5 &&
            commandApdu[0] == 0x00.toByte() &&
            commandApdu[1] == 0xA4.toByte() &&
            commandApdu[2] == 0x04.toByte() &&
            commandApdu[3] == 0x00.toByte()
    }

    private fun isGetDataApdu(commandApdu: ByteArray): Boolean {
        return commandApdu.size >= 5 &&
            commandApdu[0] == 0x80.toByte() &&
            commandApdu[1] == 0xCA.toByte()
    }

    private fun defaultPayload(): String {
        return "{\"userId\":\"user_123\",\"action\":\"receive\",\"timestamp\":\"\"}"
    }

    companion object {
        const val PREFS_NAME = "tapit_peer_hce"
        const val PREF_KEY_PAYLOAD = "peer_payload"
        val AID: ByteArray = byteArrayOf(0xF0.toByte(), 0x01, 0x02, 0x03, 0x04, 0x05)
        val GET_DATA_APDU: ByteArray = byteArrayOf(0x80.toByte(), 0xCA.toByte(), 0x00, 0x00, 0x00)
        private val SUCCESS_SW: ByteArray = byteArrayOf(0x90.toByte(), 0x00)
        private val UNKNOWN_COMMAND_SW: ByteArray = byteArrayOf(0x6D.toByte(), 0x00)
    }
}