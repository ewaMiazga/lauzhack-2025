# 🔍 Debug Logging Guide

## Added Comprehensive Logging to backend.py

I've added detailed logging/print statements throughout the backend to help you identify exactly where errors occur.

---

## 📍 Logging Added to These Functions:

### 1. **`encode_image_to_base64()`**

**Logs Added:**
- ✅ Checking if image file exists
- ✅ Image file size in KB
- ✅ Bytes read from file
- ✅ Base64 encoding success with character count
- ❌ Error logging if encoding fails

**Example Output:**
```
🔍 [DEBUG] Checking if image file exists: C:\...\satellite_data\sentinel2_20231007.jpg
✅ Image file exists
📊 Image file size: 1234567 bytes (1205.63 KB)
📖 Read 1234567 bytes from file
✅ Successfully encoded to base64 (1646089 chars)
```

---

### 2. **`analyze_image_with_vlm()`**

**Logs Added:**
- ✅ Function start with parameters
- ✅ Step 1: Encoding image to base64
- ✅ Step 2: Building messages list
- ✅ Step 3: Adding current message with image
- ✅ Step 4: Calling Together AI Vision API
- ✅ Step 5: Collecting streaming response (every 10th chunk)
- ✅ Final response statistics
- ⚠️ Warning if response is empty
- ❌ Full exception details with traceback

**Example Output:**
```
🔍 [DEBUG] Starting analyze_image_with_vlm...
   Image path: C:\...\satellite_data\sentinel2_20231007.jpg
   Prompt length: 456 characters
   Has conversation history: False
   
   🔍 [DEBUG] Step 1: Encoding image to base64...
   ✅ Image encoded successfully (length: 1646089 chars)
   
   🔍 [DEBUG] Step 2: Building messages list...
   🔍 [DEBUG] Step 3: Adding current message with image...
   ✅ Messages list built (total messages: 1)
   
   🔍 [DEBUG] Step 4: Calling Together AI Vision API...
   Model: meta-llama/Llama-Vision-Free
   ✅ API call initiated, starting to stream response...
   
   🔍 [DEBUG] Step 5: Collecting streaming response...
   📥 Received chunk 10 (total length: 125 chars)
   📥 Received chunk 20 (total length: 287 chars)
   📥 Received chunk 30 (total length: 421 chars)
   
   ✅ Streaming complete! Received 35 chunks
   📝 Final response length: 489 characters
```

---

### 3. **`/api/fetch-data` Endpoint**

**Logs Added:**
- ✅ Endpoint called notification
- ✅ JSON parsing status
- ✅ Request details (region, dates, layers)
- ✅ Directory scanning
- ✅ Each image found with size
- ✅ Success/failure summary
- ❌ Full exception details

**Example Output:**
```
================================================================================
📡 [API] /api/fetch-data endpoint called
================================================================================
🔍 [DEBUG] Parsing request JSON...
✅ Request JSON parsed

📊 Request details:
   Region: N:46.0, S:45.5, E:13.5, W:13.0
   Date Range: 2023-10-01 to 2023-10-31
   Layers: truecolor, nbr

🔍 [DEBUG] Scanning for satellite images...
   Directory: C:\projects\lauzhack-2025\satellite_data
   Total files in directory: 1
   ✅ Found image: sentinel2_20231007.jpg (1205.63 KB)

✅ [SUCCESS] Found 1 satellite image(s)
================================================================================
```

---

### 4. **`/api/analyze` Endpoint**

**Logs Added:**
- ✅ Endpoint called notification
- ✅ Step 1: Parsing request data with all keys
- ✅ Step 2: Extracting all fields (prompt, region, dates, layers, history)
- ✅ Field validation errors
- ✅ Step 3: Looking for satellite images
- ✅ Step 4: Selecting image with full path
- ✅ Step 5: Building enhanced prompt
- ✅ Step 6: Calling AI analysis function
- ✅ Step 7: Returning JSON response
- ❌ Critical error details with full traceback

**Example Output:**
```
================================================================================
🤖 [API] /api/analyze endpoint called
================================================================================
🔍 [DEBUG] Step 1: Parsing request data...
✅ Request JSON parsed successfully
   Keys in request: ['prompt', 'region', 'dateRange', 'layers', 'conversationHistory']

🔍 [DEBUG] Step 2: Extracting fields from request...
   ✅ Prompt: What is the burn severity in this region?
   ✅ Region: {'north': 46.0, 'south': 45.5, 'east': 13.5, 'west': 13.0}
   ✅ Date range: {'start': '2023-10-01', 'end': '2023-10-31'}
   ✅ Layers: ['nbr', 'ndvi']
   ✅ Conversation history length: 0

🔍 [DEBUG] Step 3: Looking for satellite images...
   Scanning directory: C:\projects\lauzhack-2025\satellite_data
   Found 1 total files in directory
   Found 1 image files: ['sentinel2_20231007.jpg']

🔍 [DEBUG] Step 4: Selecting image to analyze...
   ✅ Selected image: sentinel2_20231007.jpg
   Full path: C:\projects\lauzhack-2025\satellite_data\sentinel2_20231007.jpg

🔍 [DEBUG] Step 5: Building enhanced prompt...
   ✅ Enhanced prompt built (567 characters)

🔍 [DEBUG] Step 6: Calling AI analysis function...
   [... analyze_image_with_vlm logs appear here ...]

✅ [SUCCESS] Analysis complete!
   Response length: 489 characters
   First 100 chars: Based on the satellite imagery, I can observe several key features...

🔍 [DEBUG] Step 7: Returning JSON response...
   ✅ Response prepared, sending to client...
================================================================================
```

---

## 🎯 How to Use This Logging

### **When You Run the Backend:**

1. **Start the server:**
   ```bash
   python backend.py
   ```

2. **Watch the terminal** - You'll see exactly:
   - Which endpoint is called
   - What data is received
   - Every step of processing
   - Where errors occur (if any)

### **If You See an Error:**

The logs will show you **EXACTLY** where it happened:

**Example - If image is missing:**
```
❌ [ERROR] Image file not found!
FileNotFoundError: Image not found: C:\...\satellite_data\missing.jpg
```

**Example - If API call fails:**
```
❌ [ERROR] Exception in analyze_image_with_vlm:
   Error type: APIError
   Error message: Invalid API key
   Traceback:
   [full Python traceback here]
```

**Example - If JSON parsing fails:**
```
❌ [ERROR] Request JSON is None!
```

---

## 🔍 Finding the Error

### **Step-by-Step Debugging:**

1. **Look for the last ✅ (success) log**
   - This tells you what worked

2. **Look for the first ❌ (error) log**
   - This tells you what failed

3. **Check the error type and message**
   - FileNotFoundError → Image missing
   - APIError → Together AI issue
   - JSONDecodeError → Request format issue
   - etc.

4. **Read the traceback**
   - Shows exact line number where error occurred

---

## 📊 Common Error Patterns

### **Pattern 1: No Response from AI**
```
✅ API call initiated, starting to stream response...
🔍 [DEBUG] Step 5: Collecting streaming response...
✅ Streaming complete! Received 0 chunks
⚠️ WARNING: Response text is empty!
```
**Cause:** API might be rate-limited or image too large

---

### **Pattern 2: Image Not Found**
```
🔍 [DEBUG] Step 3: Looking for satellite images...
   Found 0 image files: []
❌ [ERROR] No satellite images available!
```
**Cause:** satellite_data/ directory is empty

---

### **Pattern 3: API Authentication Error**
```
🔍 [DEBUG] Step 4: Calling Together AI Vision API...
❌ [ERROR] Exception in analyze_image_with_vlm:
   Error type: AuthenticationError
   Error message: Invalid API key
```
**Cause:** TOGETHER_API_KEY is missing or invalid

---

## 🎯 Quick Reference

### **Logging Levels:**

- 🔍 `[DEBUG]` - Normal processing steps
- ✅ Success/confirmation
- ⚠️ `[WARNING]` - Potential issues
- ❌ `[ERROR]` - Errors that were handled
- ❌❌❌ `[CRITICAL ERROR]` - Unhandled exceptions

### **Key Sections:**

- `=====` lines → Major section boundaries
- `Step 1, 2, 3...` → Sequential processing steps
- Indented lines → Details within a step

---

## 💡 Tips

1. **Copy the entire terminal output** when reporting issues
2. **Look for the pattern** of logs - where did it stop?
3. **Check file paths** - are they correct?
4. **Verify API key** - is it set in .env?
5. **Check image files** - do they exist and are they valid?

---

## ✅ Next Steps

1. **Restart your backend server:**
   ```bash
   python backend.py
   ```

2. **Try the prompt again** in the web interface

3. **Watch the terminal output** carefully

4. **Share the logs** if you need help - they now contain all the info needed!

---

**You now have comprehensive logging at every critical point!** 🎉

The logs will tell you exactly where the error is occurring.

