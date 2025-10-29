# 🎨 Frontend Implementation Guide for AI Enhancement (Multilingual)

## Overview
The AI enhancement feature enhances thesis titles in **3 languages** (English, Kazakh, Russian) and the description using Google's Gemini AI. The backend processes everything in a single API call and returns all enhanced fields.

## Endpoint Details

**URL:** `POST /api/topics/enhance-description/`  
**Authentication:** Required (Bearer Token in Authorization header)

---

## Request Payload

Send a JSON object with up to 4 fields:

### Required Field:
- **`description`** (string, required)
  - The thesis description text to enhance
  - Must be between 10 and 5000 characters
  - Should be trimmed (no leading/trailing whitespace)

### Optional Fields:
- **`title_en`** (string, optional)
  - English title (max 500 characters)
  - Used as reference for enhancement
  
- **`title_kz`** (string, optional)
  - Kazakh title (max 500 characters)
  - Used as reference for translation
  
- **`title_ru`** (string, optional)
  - Russian title (max 500 characters)
  - Used as reference for translation

### Example Request:
```json
{
  "description": "This research studies computer vision models for early cancer detection",
  "title_en": "CV ML cancer detector",
  "title_kz": "Компьютерлік көру қатерлі ісік детекторы",
  "title_ru": "Детектор рака с помощью компьютерного зрения"
}
```

---

## Response Handling

### Success Response (200 OK):
Returns a JSON object with all 4 enhanced fields:

```json
{
  "enhanced_title_en": "Computer Vision-Based Machine Learning System for Early-Stage Cancer Detection",
  "enhanced_title_kz": "Қатерлі ісіктің ерте кезеңін анықтау үшін компьютерлік көруге негізделген машиналық оқыту жүйесі",
  "enhanced_title_ru": "Система машинного обучения на основе компьютерного зрения для раннего обнаружения рака",
  "enhanced_description": "This research focuses on developing an advanced computer vision-based machine learning system specifically designed for the early detection of cancer. The study aims to create a robust diagnostic tool that can identify cancerous tissues at stage 0, potentially revolutionizing early cancer screening..."
}
```

**Response Fields:**
- `enhanced_title_en`: AI-enhanced English title (10-15 words, academic)
- `enhanced_title_kz`: Translated and enhanced Kazakh title
- `enhanced_title_ru`: Translated and enhanced Russian title
- `enhanced_description`: Enhanced description (2-4 paragraphs, academic tone)

### Error Responses:

#### 400 Bad Request - Validation Errors
```json
{
  "error": "Description is required"
}
```

Possible validation errors:
- `"Description is required"` - No description provided
- `"Description is too short (minimum 10 characters)"` - Description < 10 chars
- `"Description is too long (maximum 5000 characters)"` - Description > 5000 chars
- `"English title is too long (maximum 500 characters)"` - title_en > 500 chars
- `"Kazakh title is too long (maximum 500 characters)"` - title_kz > 500 chars
- `"Russian title is too long (maximum 500 characters)"` - title_ru > 500 chars

#### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```
- Token is missing or invalid
- Redirect user to login

#### 500 Internal Server Error
```json
{
  "error": "Failed to enhance thesis content. Please try again later."
}
```
- Gemini API issues
- Network problems
- Show user-friendly error message

---

## Implementation Guide

### Step 1: Prepare Your Data

```javascript
// Get values from your form
const description = project.value.description.trim();
const titleEn = project.value.title_en?.trim() || '';
const titleKz = project.value.title_kz?.trim() || '';
const titleRu = project.value.title_ru?.trim() || '';
```

### Step 2: Validate Before Sending

```javascript
// Pre-validation (optional but recommended)
if (!description || description.length < 10) {
  alert("Please enter a description (at least 10 characters).");
  return;
}

if (description.length > 5000) {
  alert("Description is too long (maximum 5000 characters).");
  return;
}
```

### Step 3: Make the API Request

```javascript
const enhanceContent = async () => {
  // Set loading state
  isEnhancing.value = true;

  try {
    const response = await axios.post(
      `${apiConfig.baseURL}/api/topics/enhance-description/`,
      {
        description: project.value.description.trim(),
        title_en: project.value.title_en?.trim() || undefined,
        title_kz: project.value.title_kz?.trim() || undefined,
        title_ru: project.value.title_ru?.trim() || undefined,
      },
      {
        headers: { 
          Authorization: `Bearer ${authStore.token}`,
        },
      }
    );

    // Update all fields with enhanced content
    if (response.data) {
      project.value.title_en = response.data.enhanced_title_en;
      project.value.title_kz = response.data.enhanced_title_kz;
      project.value.title_ru = response.data.enhanced_title_ru;
      project.value.description = response.data.enhanced_description;
      
      // Optional: Show success message
      console.log("✅ Content enhanced successfully!");
    }
  } catch (err) {
    console.error("Failed to enhance content", err.response?.data || err);
    
    // Show user-friendly error message
    const errorMessage = err.response?.data?.error || 
                        "Failed to enhance content. Please try again.";
    alert(errorMessage);
  } finally {
    // Always reset loading state
    isEnhancing.value = false;
  }
};
```

### Step 4: Update UI Elements

```vue
<template>
  <div class="thesis-form">
    <!-- English Title -->
    <input 
      v-model="project.title_en" 
      placeholder="English Title"
      maxlength="500"
    />
    
    <!-- Kazakh Title -->
    <input 
      v-model="project.title_kz" 
      placeholder="Қазақша тақырып"
      maxlength="500"
    />
    
    <!-- Russian Title -->
    <input 
      v-model="project.title_ru" 
      placeholder="Русское название"
      maxlength="500"
    />
    
    <!-- Description -->
    <textarea 
      v-model="project.description" 
      placeholder="Description"
      maxlength="5000"
    />
    
    <!-- AI Enhance Button -->
    <button 
      @click="enhanceContent"
      :disabled="isEnhancing || !project.description"
    >
      <span v-if="isEnhancing">
        🤖 Enhancing...
      </span>
      <span v-else>
        ✨ AI Enhance
      </span>
    </button>
  </div>
</template>
```

---

## UI/UX Best Practices

### 1. Loading State
```javascript
// Show clear feedback during processing
isEnhancing.value = true; // Disable button, show spinner

// Typical response time: 3-7 seconds
// Consider showing a progress message:
// "Enhancing titles and description in 3 languages..."
```

### 2. Pre-validation
```javascript
// Validate before API call to avoid unnecessary requests
if (!description.trim()) {
  alert("Please enter a description first.");
  return;
}
```

### 3. Error Handling
```javascript
// Show specific error messages from API
const errorMessage = err.response?.data?.error || 
                    "Failed to enhance content. Please try again.";
alert(errorMessage);
```

### 4. User Feedback
```javascript
// After successful enhancement:
// - Show success toast/notification
// - Highlight changed fields briefly
// - Allow undo if needed
```

### 5. Optional: Undo Feature
```javascript
// Save original values before enhancement
const originalContent = {
  title_en: project.value.title_en,
  title_kz: project.value.title_kz,
  title_ru: project.value.title_ru,
  description: project.value.description,
};

// Provide undo button
const undoEnhancement = () => {
  Object.assign(project.value, originalContent);
};
```

---

## Complete Example (Vue 3 Composition API)

```javascript
import { ref } from 'vue';
import axios from 'axios';

const project = ref({
  title_en: '',
  title_kz: '',
  title_ru: '',
  description: '',
});

const isEnhancing = ref(false);
const originalContent = ref(null);

const enhanceContent = async () => {
  // Pre-validation
  if (!project.value.description?.trim()) {
    alert("Please enter a description first.");
    return;
  }

  if (project.value.description.length < 10) {
    alert("Description must be at least 10 characters.");
    return;
  }

  // Save original for undo
  originalContent.value = { ...project.value };

  // Set loading state
  isEnhancing.value = true;

  try {
    const response = await axios.post(
      `${apiConfig.baseURL}/api/topics/enhance-description/`,
      {
        description: project.value.description.trim(),
        title_en: project.value.title_en?.trim() || undefined,
        title_kz: project.value.title_kz?.trim() || undefined,
        title_ru: project.value.title_ru?.trim() || undefined,
      },
      {
        headers: { Authorization: `Bearer ${authStore.token}` },
      }
    );

    // Update all fields
    if (response.data) {
      project.value.title_en = response.data.enhanced_title_en;
      project.value.title_kz = response.data.enhanced_title_kz;
      project.value.title_ru = response.data.enhanced_title_ru;
      project.value.description = response.data.enhanced_description;
      
      // Show success feedback
      console.log("✅ Content enhanced successfully!");
      // Optional: showToast("Content enhanced successfully!", "success");
    }
  } catch (err) {
    console.error("Enhancement failed:", err.response?.data || err);
    
    const errorMessage = err.response?.data?.error || 
                        "Failed to enhance content. Please try again.";
    alert(errorMessage);
  } finally {
    isEnhancing.value = false;
  }
};

const undoEnhancement = () => {
  if (originalContent.value) {
    project.value = { ...originalContent.value };
    originalContent.value = null;
  }
};
```

---

## Testing

### Test Case 1: All Fields Provided
```javascript
{
  "description": "AI for cancer detection",
  "title_en": "Cancer Detection System",
  "title_kz": "Қатерлі ісікті анықтау жүйесі",
  "title_ru": "Система обнаружения рака"
}
```

### Test Case 2: Only English Title + Description
```javascript
{
  "description": "AI for cancer detection",
  "title_en": "Cancer Detection System"
  // title_kz and title_ru will be generated
}
```

### Test Case 3: Only Description
```javascript
{
  "description": "This research studies computer vision for early cancer detection"
  // All 3 titles will be generated from description
}
```

---

## Important Notes

### ✅ What Happens:
1. **English title** is enhanced or generated if not provided
2. **Description** is enhanced to align with English title
3. **Kazakh & Russian titles** are translated from enhanced English title
4. All processing happens in **one API call** (3-7 seconds)

### ⚠️ Limitations:
- **Response time**: 3-7 seconds (show loading indicator)
- **Rate limits**: Free tier = 15 requests/minute
- **Maximum lengths**: Description 5000 chars, titles 500 chars each
- **Authentication**: JWT token required

### 💡 Tips:
- Provide at least the English title for better results
- All titles are optional but recommended
- AI results may vary slightly each time
- Consider network timeout of 15-30 seconds
- Save original content for undo feature

---

## Troubleshooting

### Issue: "Description is required"
**Solution:** Ensure description field is not empty before calling API

### Issue: Network timeout
**Solution:** Increase axios timeout to 30 seconds:
```javascript
axios.post(url, data, { 
  timeout: 30000,
  headers: {...} 
})
```

### Issue: 401 Unauthorized
**Solution:** Check if JWT token is valid and not expired

### Issue: Slow response
**Solution:** This is normal (3-7 seconds). Show proper loading indicator

---

## Summary

**Single API call enhances:**
- ✅ English title (enhanced or generated)
- ✅ Kazakh title (translated from enhanced English)
- ✅ Russian title (translated from enhanced English)
- ✅ Description (enhanced, aligned with title)

**Frontend needs to:**
- Send 1-4 fields (description required, titles optional)
- Handle 3-7 second response time
- Update all 4 fields in the form
- Show proper loading states and errors

That's it! 🎉
