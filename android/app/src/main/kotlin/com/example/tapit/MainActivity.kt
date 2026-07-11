package com.example.tapit

import android.nfc.NfcAdapter
import android.nfc.Tag
import android.nfc.tech.IsoDep
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import java.nio.charset.StandardCharsets

class MainActivity : FlutterActivity() {
	private val channelName = "tapit/nfc"
	private var pendingReadResult: MethodChannel.Result? = null
	private var nfcAdapter: NfcAdapter? = null
	private var readerModeEnabled = false

	override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
		super.configureFlutterEngine(flutterEngine)

		nfcAdapter = NfcAdapter.getDefaultAdapter(this)

		MethodChannel(flutterEngine.dartExecutor.binaryMessenger, channelName)
			.setMethodCallHandler { call, result ->
				when (call.method) {
					"isAvailable" -> result.success(nfcAdapter != null)

					"setPeerPayload" -> {
						val payload = call.argument<String>("payload") ?: ""
						getSharedPreferences(PeerHostApduService.PREFS_NAME, MODE_PRIVATE)
							.edit()
							.putString(PeerHostApduService.PREF_KEY_PAYLOAD, payload)
							.apply()
						result.success(true)
					}

					"startPeerRead" -> startPeerRead(result)

					"stopPeerRead" -> {
						stopPeerRead()
						result.success(true)
					}

					else -> result.notImplemented()
				}
			}
	}

	override fun onResume() {
		super.onResume()
		if (readerModeEnabled) {
			enableReaderMode()
		}
	}

	override fun onPause() {
		disableReaderMode()
		super.onPause()
	}

	private fun startPeerRead(result: MethodChannel.Result) {
		if (nfcAdapter == null) {
			result.error("NFC_UNAVAILABLE", "NFC is not available on this device", null)
			return
		}

		if (pendingReadResult != null) {
			result.error("NFC_BUSY", "An NFC read is already in progress", null)
			return
		}

		pendingReadResult = result
		readerModeEnabled = true
		enableReaderMode()
	}

	private fun enableReaderMode() {
		val adapter = nfcAdapter ?: return
		adapter.enableReaderMode(
			this,
			{ tag -> handleTagDiscovered(tag) },
			NfcAdapter.FLAG_READER_NFC_A or
				NfcAdapter.FLAG_READER_NFC_B or
				NfcAdapter.FLAG_READER_SKIP_NDEF_CHECK,
			null
		)
	}

	private fun disableReaderMode() {
		nfcAdapter?.disableReaderMode(this)
		readerModeEnabled = false
	}

	private fun stopPeerRead() {
		pendingReadResult = null
		disableReaderMode()
	}

	private fun handleTagDiscovered(tag: Tag) {
		Thread {
			try {
				val isoDep = IsoDep.get(tag)
					?: throw IllegalStateException("Nearby device does not support NFC peer exchange")

				isoDep.connect()

				val selectApdu = buildSelectApdu(PeerHostApduService.AID)
				val selectResponse = isoDep.transceive(selectApdu)
				ensureSuccess(selectResponse, "Receiver did not accept NFC session")

				val readResponse = isoDep.transceive(PeerHostApduService.GET_DATA_APDU)
				ensureSuccess(readResponse, "Receiver did not return a payload")

				val payloadBytes = readResponse.copyOfRange(0, readResponse.size - 2)
				val payload = String(payloadBytes, StandardCharsets.UTF_8)

				isoDep.close()

				runOnUiThread {
					pendingReadResult?.success(payload)
					pendingReadResult = null
					disableReaderMode()
				}
			} catch (e: Exception) {
				runOnUiThread {
					pendingReadResult?.error("NFC_READ_FAILED", e.message, null)
					pendingReadResult = null
					disableReaderMode()
				}
			}
		}.start()
	}

	private fun buildSelectApdu(aid: ByteArray): ByteArray {
		val header = byteArrayOf(0x00, 0xA4.toByte(), 0x04, 0x00, aid.size.toByte())
		return header + aid + byteArrayOf(0x00)
	}

	private fun ensureSuccess(response: ByteArray, message: String) {
		if (response.size < 2) {
			throw IllegalStateException(message)
		}

		val sw1 = response[response.size - 2]
		val sw2 = response[response.size - 1]
		if (sw1 != 0x90.toByte() || sw2 != 0x00.toByte()) {
			throw IllegalStateException(message)
		}
	}
}
