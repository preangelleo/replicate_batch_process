# Image Models Configuration  
REPLICATE_MODELS = {
    'qwen/qwen-image': {
        'model_type': 'image',
        'price': 0.025,
        'url': 'https://replicate.com/qwen/qwen-image',
        'use_case': 'text_to_image',
        'specialized': 'text_rendering',
        'scenario': 'cover_image',
        'reference_image': False,
        'description': 'An image generation foundation model in the Qwen series that achieves significant advances in complex text rendering.',
        'supported_params': {
            'go_fast': {'type': 'bool', 'default': True},
            'guidance': {'type': 'float', 'default': 4, 'range': [0, 10]},
            'image_size': {'type': 'select', 'default': 'optimize_for_quality', 'options': ['optimize_for_quality', 'optimize_for_speed']},
            'lora_scale': {'type': 'float', 'default': 1, 'range': [0, 2]},
            'aspect_ratio': {'type': 'select', 'default': '16:9', 'options': ['1:1', '16:9', '9:16', '3:4', '4:3']},
            'output_format': {'type': 'select', 'default': 'webp', 'options': ['webp', 'jpg', 'png']},
            'enhance_prompt': {'type': 'bool', 'default': False},
            'output_quality': {'type': 'int', 'default': 80, 'range': [0, 100]},
            'negative_prompt': {'type': 'str', 'default': ''},
            'num_inference_steps': {'type': 'int', 'default': 50, 'range': [1, 100]}
        }
    },
    'black-forest-labs/flux-kontext-max': {
        'model_type': 'image',
        'price': 0.08,
        'url': 'https://replicate.com/black-forest-labs/flux-kontext-max',
        'use_case': 'text_to_image',
        'specialized': 'image_to_image',
        'scenario': 'character_consistency',
        'reference_image': True,
        'description': 'A premium text-based image editing model that delivers maximum performance and improved typography generation for transforming images through natural language prompts.',
        'supported_params': {
            'input_image': {'type': 'file', 'default': None, 'description': 'Reference image for editing (accepts file path, URL, or file object)'},
            'aspect_ratio': {'type': 'select', 'default': 'match_input_image', 'options': ['match_input_image', '1:1', '16:9', '9:16', '4:3', '3:4', '21:9', '9:21']},
            'output_format': {'type': 'select', 'default': 'png', 'options': ['jpg', 'png']},
            'seed': {'type': 'int', 'default': None},
            'safety_tolerance': {'type': 'int', 'default': 2, 'range': [0, 6]},
            'prompt_upsampling': {'type': 'bool', 'default': False}
        }
    },
    'black-forest-labs/flux-dev': {
        'model_type': 'image',
        'price': 0.025,
        'url': 'https://replicate.com/black-forest-labs/flux-dev',
        'use_case': 'text_to_image',
        'specialized': 'little_censorship_fast',
        'scenario': 'fallback_from_flux-kontext-max',
        'reference_image': False,
        'description': 'A 12 billion parameter rectified flow transformer capable of generating images from text descriptions.',
        'supported_params': {
            'seed': {'type': 'int', 'default': None},
            'go_fast': {'type': 'bool', 'default': True},
            'guidance': {'type': 'float', 'default': 3, 'range': [0, 10]},
            'megapixels': {'type': 'select', 'default': '1', 'options': ['1', '0.25']},
            'num_outputs': {'type': 'int', 'default': 1, 'range': [1, 4]},
            'aspect_ratio': {'type': 'select', 'default': '1:1', 'options': ['1:1', '16:9', '9:16', '3:4', '4:3']},
            'output_format': {'type': 'select', 'default': 'webp', 'options': ['webp', 'jpg', 'png']},
            'output_quality': {'type': 'int', 'default': 80, 'range': [0, 100]},
            'prompt_strength': {'type': 'float', 'default': 0.8, 'range': [0, 1]},
            'num_inference_steps': {'type': 'int', 'default': 28, 'range': [1, 50]},
            'disable_safety_checker': {'type': 'bool', 'default': False}
        }
    },
    'google/imagen-4-ultra': {
        'model_type': 'image',
        'price': 0.06,
        'url': 'https://replicate.com/google/imagen-4-ultra',
        'use_case': 'text_to_image',
        'specialized': 'high_quality_detailed_images',
        'scenario': 'premium_quality_generation',
        'reference_image': False,
        'description': "Google's Imagen 4 Ultra is a state-of-the-art image generation model that can create high-quality, detailed images from text prompts.",
        'supported_params': {
            'aspect_ratio': {'type': 'select', 'default': '1:1', 'options': ['1:1', '9:16', '16:9', '3:4', '4:3']},
            'output_format': {'type': 'select', 'default': 'jpg', 'options': ['jpg', 'png']},
            'safety_filter_level': {'type': 'select', 'default': 'block_only_high', 'options': ['block_low_and_above', 'block_medium_and_above', 'block_only_high']}
        }
    },
    'google/veo-3-fast': {
        'model_type': 'video',
        'price': 3.32, # $3.32 per call
        'url': 'https://replicate.com/google/veo-3-fast',
        'use_case': 'text_to_video',
        'specialized': 'fast_high_quality_responses',
        'scenario': 'prompt_enhancement_and_conversation',
        'reference_image': True,
        'description': "A faster and cheaper version of Google's Veo 3 video model, with audio",
        'supported_params': {
            'image': {'type': 'file', 'default': None, 'description': 'Input image to start generating from (ideal: 1280x720)'},
            'resolution': {'type': 'select', 'default': '720p', 'options': ['720p', '1080p']},
            'negative_prompt': {'type': 'str', 'default': '', 'description': 'Description of what to discourage in the generated video'},
            'seed': {'type': 'int', 'default': None, 'description': 'Random seed for reproducibility'}
        }
    },
    'kwaivgi/kling-v2.1-master': {
        'model_type': 'video',
        'price': 0.28, # $0.28 per second of output video
        'url': 'https://replicate.com/kwaivgi/kling-v2.1-master',
        'use_case': 'text_to_video',
        'specialized': '1080p_video_generation',
        'scenario': 'high_quality_video_creation',
        'reference_image': True,
        'description': "Kling v2.1 Master video generation model supporting 1080p videos with 5 or 10-second durations",
        'supported_params': {
            'duration': {'type': 'int', 'default': 5, 'options': [5, 10], 'description': 'Duration of the video in seconds'},
            'start_image': {'type': 'file', 'default': None, 'description': 'First frame of the video (accepts file path, URL, or file object)'},
            'aspect_ratio': {'type': 'select', 'default': '16:9', 'options': ['16:9', '9:16', '1:1'], 'description': 'Aspect ratio (ignored if start_image provided)'},
            'negative_prompt': {'type': 'str', 'default': '', 'description': 'Things you do not want to see in the video'}
        }
    }
}




SYSTEM_PROMPT_STRUCTURED_IMAGE_DESCRIPTION = """# Image Description Refinement System Prompt

User will send an image prompt or idea for image generation from a storyboard script. Refine the prompt with the following image generation best practices. Respond only with the refined image description in plain text format with proper structure using line breaks and spacing, no JSON format.

## Core Mission
Transform context-dependent storyboard descriptions into completely independent, high-quality image generation prompts that AI image models can accurately understand and generate without any external context.

## CRITICAL: Art Style Preservation and Enhancement
**EXTREMELY IMPORTANT**: The artistic style mentioned in the prompt is PARAMOUNT and must be preserved, clarified, and emphasized above all else. And never show/display any words in this image (if the original prompt contains image display, remove them; change the settings a little bit.).

### Style Clarification Rules:
1. **Always identify the mentioned art style** in the original prompt (e.g., "3D Rendering", "Anime Style", "Watercolor")
2. **Clarify ambiguous style terms**:
   - "3D Rendering" → Specify as "3D animated cartoon style like Pixar/Disney animation" NOT "photorealistic 3D render"
   - "Anime Style" → "Japanese anime art style with characteristic anime features"
   - "Comic Book Style" → "American comic book illustration with bold lines and vibrant colors"
   - "Digital Painting" → Specify the type: "stylized digital painting" or "painterly digital art"
3. **Reinforce the style throughout the description** - mention it at least 2-3 times in different contexts
4. **Add style-specific characteristics**:
   - For animated styles: "cartoon proportions", "stylized features", "non-photorealistic"
   - For artistic styles: mention texture, brushwork, color approach
5. **Explicitly reject photorealism** when the style is meant to be animated or stylized

## Critical Issues to Address

**IMPORTANT**: Sometimes user input comes from a storyboard scene description that may lack context. Previous team members may not have considered that image generation models only see this specific prompt and don't know the context. We must improve this. For example, if the user input says "he does something," our refined version cannot use "he" because the image model doesn't know who "he" is. Instead, we must use precise descriptions like "an Asian woman," "a Black man," or "a middle-aged man" to control the image output accurately.

## Prompting Best Practices

### Be Specific
- Use clear, detailed language with exact colors and descriptions
- Avoid vague terms like "make it better"
- Name subjects directly: "the woman with short black hair" vs. "she"

### Preserve Intentionally
- Specify what should stay the same: "while keeping the same facial features"
- Use "maintain the original composition" to preserve layout
- For background changes: "Change the background to a beach while keeping the person in the exact same position"

### Text Editing Tips
- Use quotation marks: "replace 'old text' with 'new text'"
- Stick to readable fonts
- Match text length when possible to preserve layout

### Style Transfer
- Be specific about artistic styles: "impressionist painting" not "artistic"
- Reference known movements: "Renaissance" or "1960s pop art"
- Describe key traits: "visible brushstrokes, thick paint texture"

### Complex Edits
- Break into smaller steps for better results
- Start simple and iterate
- Use descriptive action verbs instead of "transform" for more control

## Additional Refinement Guidelines

### 1. Eliminate Pronoun Dependencies
- **Problem**: Original descriptions may use "he," "she," "this person," "the character"
- **Solution**: Replace with specific descriptions:
  - "he holds a book" → "a friendly scarecrow character wearing a scholar's hat holds a book"
  - "her smile" → "the woman's enigmatic smile"
  - "this building" → "a 15th-century Florentine cathedral"

### 2. Character Name Reduction
- **Important**: Do NOT include character names unless absolutely necessary for context
- Focus on visual appearance rather than identity
- Replace "Leonardo da Vinci" with "a Renaissance-era man with long white beard and hair"
- Replace "Mino Haythorn" with "a friendly scarecrow character wearing a scholar's hat"

### 3. Minimize Text Generation Requests
- **Critical**: AVOID adding text generation prompts unless the original description specifically requires text in the image
- Image-generated text is often inaccurate and illegible
- If text must be included, keep it minimal and use simple, readable fonts
- Focus on visual storytelling rather than text-based information

### 4. Complete Scene Context
- Add historical period and geographical context
- Describe environmental atmosphere and lighting conditions
- Include important props and background elements
- Maintain "Stage Theatre Illustration" style consistency

### 5. Character Appearance Standardization
Create detailed physical descriptions for recurring characters:
- Physical features (age, build, facial characteristics)
- Clothing and accessories
- Distinctive visual markers
- Emotional expressions and body language

### 6. Technical Optimization
- Specify camera angles and composition requirements
- Identify key visual focal points
- Describe special effects (glowing, shadows, transparency)
- Ensure lighting consistency across scenes

## Output Structure

Your response should follow this structure using plain text with proper formatting:

**Main Subject:**
[Detailed description of the primary character or object]

**Setting & Environment:**
[Background, location, time period, atmosphere]

**Composition & Lighting:**
[Camera angle, lighting conditions, mood]

**Style & Details:**
[Artistic style, specific visual effects, color palette]

**Additional Elements:**
[Props, secondary characters, special effects]

## Quality Checklist
- ✅ No pronouns without clear antecedents
- ✅ No character names unless contextually essential
- ✅ Minimal or no text generation requests
- ✅ Complete visual descriptions
- ✅ Consistent artistic style specification
- ✅ Clear subject identification
- ✅ Proper lighting and atmosphere description

## Examples

### Input Example:
"Mino stands center stage and points to a diagram showing Leonardo's brain with gears and art tools."

### Output Example:
**Main Subject:**
A friendly scarecrow character made of straw with expressive, curious eyes, wearing a slightly oversized dark blue scholar's hat. The character stands confidently center stage, extending one arm to point toward a large diagram.

**Setting & Environment:**
A theatrical stage setting with warm, dramatic lighting. The stage has a scholarly atmosphere with an educational presentation backdrop.

**Composition & Lighting:**
Medium shot composition with the scarecrow character positioned center stage. Warm theatrical spotlights illuminate the scene from above, creating soft shadows and a welcoming atmosphere.

**Style & Details:**
Stage Theatre Illustration style with clean lines and educational diagram aesthetics. The diagram shows a stylized cross-section of a human brain with intricate mechanical gears, paintbrushes, and scientific instruments interconnected within the brain structure.

**Additional Elements:**
The pointing gesture draws attention to the educational diagram. The overall scene has a whimsical yet scholarly tone, combining theatrical presentation with scientific illustration elements.

---

### Example:
User: "He paints while observing birds in flight, taking notes about their wing movements."

Assistant:
**Main Subject:**
A Renaissance-era man with long flowing white beard and hair, wearing typical 15th-century Florentine robes in earth tones. He holds a paintbrush in one hand and a quill pen in the other, his expression focused and intensely curious.

**Setting & Environment:**
An outdoor countryside setting with rolling hills and clear blue skies. Multiple birds are captured mid-flight across the sky, showing various wing positions and flight patterns.

**Composition & Lighting:**
Wide shot showing the man positioned in the lower third of the frame, with the sky and flying birds occupying the upper portion. Natural daylight with soft, diffused lighting creates realistic shadows and highlights.

**Style & Details:**
Stage Theatre Illustration style with Renaissance painting influences. The birds are depicted with scientific accuracy, showing detailed wing structures and aerodynamic positions. Warm color palette with natural earth tones and sky blues.

**Additional Elements:**
An open notebook or sketchpad visible nearby with partially completed drawings of bird anatomy and wing studies. The scene captures a moment of scientific observation and artistic creation combined.

Transform the input image description according to these guidelines into an optimized image generation prompt using the structure above.
"""
