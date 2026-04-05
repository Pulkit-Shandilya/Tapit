# NFC Payment System - API Testing with cURL

This file contains example cURL commands for testing all API endpoints.

## Prerequisites
- Flask server running: `python app.py`
- cURL installed (included with Windows 10+)
- Or use git-bash, WSL, or install cURL separately

## 1. USER MANAGEMENT

### Create User
```bash
curl -X POST http://localhost:5000/api/user/create ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\": \"USER001\"}"
```

### Get User Details
```bash
curl http://localhost:5000/api/user/USER001
```

---

## 2. MERCHANT MANAGEMENT

### Create Merchant
```bash
curl -X POST http://localhost:5000/api/merchant/create ^
  -H "Content-Type: application/json" ^
  -d "{\"merchant_id\": \"MERCHANT001\"}"
```

### Get Merchant Details
```bash
curl http://localhost:5000/api/merchant/MERCHANT001
```

---

## 3. SMART CONTRACT

### View Smart Contract Rules
```bash
curl http://localhost:5000/api/smart-contract
```

Expected Response:
```json
{
    "max_amount": 10000,
    "valid_until": "2025-12-31",
    "description": "Smart contract enforces transaction limits and validity dates"
}
```

---

## 4. PAYMENT FLOW

### Successful Payment (Amount within limit)
```bash
curl -X POST http://localhost:5000/api/payment ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\": \"USER001\", \"merchant_id\": \"MERCHANT001\", \"amount\": 5000}"
```

### Declined Payment (Amount exceeds limit of 10000)
```bash
curl -X POST http://localhost:5000/api/payment ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\": \"USER001\", \"merchant_id\": \"MERCHANT001\", \"amount\": 15000}"
```

---

## 5. AUTHORIZATION FLOW

### Process Authorization
```bash
curl -X POST http://localhost:5000/api/authorize ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\": \"USER001\", \"amount\": 5000}"
```

---

## 6. BLOCKCHAIN LEDGERS

### View Acquiring Bank Ledger
```bash
curl http://localhost:5000/api/ledger/acquiring
```

### View Issuing Bank Ledger
```bash
curl http://localhost:5000/api/ledger/issuing
```

---

## COMPLETE WORKFLOW EXAMPLE

Execute these commands in order to test the full workflow:

```bash
REM Step 1: Create Users
curl -X POST http://localhost:5000/api/user/create ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\": \"ALICE\"}"

curl -X POST http://localhost:5000/api/user/create ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\": \"BOB\"}"

REM Step 2: Create Merchants
curl -X POST http://localhost:5000/api/merchant/create ^
  -H "Content-Type: application/json" ^
  -d "{\"merchant_id\": \"STARBUCKS\"}"

curl -X POST http://localhost:5000/api/merchant/create ^
  -H "Content-Type: application/json" ^
  -d "{\"merchant_id\": \"APPLE_STORE\"}"

REM Step 3: View Smart Contract
curl http://localhost:5000/api/smart-contract

REM Step 4: Alice pays Starbucks 2500
curl -X POST http://localhost:5000/api/payment ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\": \"ALICE\", \"merchant_id\": \"STARBUCKS\", \"amount\": 2500}"

REM Step 5: Bob pays Apple Store 7500
curl -X POST http://localhost:5000/api/payment ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\": \"BOB\", \"merchant_id\": \"APPLE_STORE\", \"amount\": 7500}"

REM Step 6: Alice authorization request (within limits)
curl -X POST http://localhost:5000/api/authorize ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\": \"ALICE\", \"amount\": 3000}"

REM Step 7: Bob tries to pay 12000 (exceeds limit)
curl -X POST http://localhost:5000/api/payment ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\": \"BOB\", \"merchant_id\": \"APPLE_STORE\", \"amount\": 12000}"

REM Step 8: View all transactions in Acquiring Bank ledger
curl http://localhost:5000/api/ledger/acquiring

REM Step 9: View all transactions in Issuing Bank ledger
curl http://localhost:5000/api/ledger/issuing

REM Step 10: Check user details
curl http://localhost:5000/api/user/ALICE
curl http://localhost:5000/api/user/BOB

REM Step 11: Check merchant details
curl http://localhost:5000/api/merchant/STARBUCKS
curl http://localhost:5000/api/merchant/APPLE_STORE
```

---

## TESTING IN POWERSHELL

If using PowerShell, replace `^` (line continuation) with backticks (`) :

```powershell
curl -X POST http://localhost:5000/api/user/create `
  -H "Content-Type: application/json" `
  -d '{"user_id": "USER001"}'
```

Or use the `-Uri` parameter:

```powershell
Invoke-WebRequest -Uri http://localhost:5000/api/user/create `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"user_id": "USER001"}' | Select-Object -ExpandProperty Content
```

---

## EXPECTED RESPONSES

### Successful Payment Response
```json
{
    "success": true,
    "transaction": {
        "user_id": "USER001",
        "merchant_id": "MERCHANT001",
        "amount": 5000,
        "timestamp": "2025-04-05T14:30:45.123456",
        "transaction_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "status": "completed",
        "acquiring_bank_status": "processed",
        "acquiring_block_hash": "a1b2c3d4e5f6...",
        "card_scheme_status": "routed",
        "issuing_bank_status": "authorized",
        "issuing_block_hash": "f1e2d3c4b5a6..."
    }
}
```

### Declined Payment Response
```json
{
    "success": false,
    "transaction": {
        "user_id": "USER001",
        "merchant_id": "MERCHANT001",
        "amount": 15000,
        "timestamp": "2025-04-05T14:35:22.654321",
        "transaction_id": "x9y8z7w6-v5u4-t3s2-r1q0-p9o8n7m6l5k4",
        "status": "declined"
    }
}
```

### Smart Contract Response
```json
{
    "max_amount": 10000,
    "valid_until": "2025-12-31",
    "description": "Smart contract enforces transaction limits and validity dates"
}
```

---

## TROUBLESHOOTING

### Connection Refused
- Ensure Flask server is running: `python app.py`
- Check the server is listening on port 5000

### Invalid JSON in cURL
- Windows cmd: Use `^` for line continuation
- PowerShell: Use backtick `` ` `` for line continuation
- Or use `Invoke-WebRequest` instead of `curl` in PowerShell

### Content-Type Error
- Always include: `-H "Content-Type: application/json"`

### Port Already in Use
- Flask is already running on another terminal
- Kill the process or use a different port by editing `app.py`
