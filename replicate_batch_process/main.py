import replicate, os, time, json
import google.generativeai as genai
from config import *
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = 'gemini-2.0-flash'

def gemini_conversation(prompt, system_prompt=None):
    """Simple Gemini conversation function"""
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    
    if system_prompt: full_prompt = f"{system_prompt}\n\nUser input: {prompt}"
    else: full_prompt = prompt
    
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"Error with Gemini API: {e}")
        return None

def optimize_prompt_with_gemini(user_prompt):
    """Optimize image prompt using Gemini with the system prompt from config"""
    optimized = gemini_conversation(user_prompt, SYSTEM_PROMPT_STRUCTURED_IMAGE_DESCRIPTION)
    if optimized:
        print("\n=== OPTIMIZED PROMPT ===")
        print(optimized)
        print("========================\n")
        return optimized
    return user_prompt

def supports_reference_image(model_name):
    """Check if a model supports reference image input"""
    model_config = REPLICATE_MODELS.get(model_name, {})
    return model_config.get('reference_image', False)

def get_image_input_param_name(model_name):
    """Get the parameter name for image input for a specific model"""
    model_config = REPLICATE_MODELS.get(model_name, {})
    supported_params = model_config.get('supported_params', {})
    
    # Common image input parameter names
    for param_name in ['input_image', 'image', 'start_image']:
        if param_name in supported_params and supported_params[param_name].get('type') == 'file':
            return param_name
    return None

def get_supported_parameters(model_name, format_for_display=True):
    """Get supported parameters for a model
    
    Args:
        model_name: Name of the model
        format_for_display: If True, returns formatted string for terminal display
                           If False, returns raw dictionary for programmatic use
    
    Returns:
        Dict or formatted string of supported parameters
    """
    model_config = REPLICATE_MODELS.get(model_name, {})
    if not model_config:
        return f"Model '{model_name}' not found in configuration"
    
    model_info = {
        'model_name': model_name,
        'model_type': model_config.get('model_type', 'unknown'),
        'price': model_config.get('price', 'unknown'),
        'description': model_config.get('description', ''),
        'reference_image_support': model_config.get('reference_image', False),
        'supported_parameters': model_config.get('supported_params', {})
    }
    
    if format_for_display:
        # Format for terminal display
        display_text = f"\n=== {model_name.upper()} PARAMETERS ===\n"
        display_text += f"Type: {model_info['model_type']}\n"
        display_text += f"Price: ${model_info['price']}\n"
        display_text += f"Reference Image Support: {'✅' if model_info['reference_image_support'] else '❌'}\n"
        display_text += f"Description: {model_info['description'][:100]}...\n\n"
        
        if model_info['supported_parameters']:
            display_text += "SUPPORTED PARAMETERS:\n"
            for param_name, param_config in model_info['supported_parameters'].items():
                display_text += f"\n• {param_name}:\n"
                display_text += f"  - Type: {param_config.get('type', 'unknown')}\n"
                display_text += f"  - Default: {param_config.get('default', 'None')}\n"
                
                if 'options' in param_config:
                    display_text += f"  - Options: {param_config['options']}\n"
                if 'range' in param_config:
                    display_text += f"  - Range: {param_config['range']}\n"
                if 'description' in param_config:
                    display_text += f"  - Description: {param_config['description']}\n"
        else:
            display_text += "No additional parameters available (uses defaults only)\n"
            
        display_text += "\n" + "="*50 + "\n"
        return display_text
    else:
        # Return raw dictionary for programmatic use
        return model_info

def show_all_models_parameters():
    """Show parameters for all available models"""
    all_models_info = {}
    for model_name in REPLICATE_MODELS.keys():
        all_models_info[model_name] = get_supported_parameters(model_name, format_for_display=False)
    return all_models_info

def check_fallback_conditions(model_name, **kwargs):
    """检查是否需要在调用前执行fallback
    
    Returns:
        tuple: (should_fallback, fallback_reason, fallback_model, mapped_kwargs)
    """
    fallback_config = FALLBACK_MODELS.get(model_name, {})
    
    # 检查reference image条件
    if 'reference_image' in fallback_config:
        # 检查是否有任何可能的reference image参数
        model_config = REPLICATE_MODELS.get(model_name, {})
        supported_params = model_config.get('supported_params', {})
        
        # 检查用户是否传入了reference image相关参数，但模型不支持
        reference_image_params = ['input_image', 'image', 'start_image', 'reference_image']
        
        for param_name in reference_image_params:
            if (param_name in kwargs and 
                kwargs[param_name] is not None and
                not model_config.get('reference_image', False)):
                
                fallback_info = fallback_config['reference_image']
                fallback_model = fallback_info['fallback_model']
                mapped_kwargs = map_parameters(model_name, fallback_model, kwargs)
                
                print(f"🔄 Reference image detected ({param_name}) but {model_name} doesn't support it")
                print(f"   Falling back to {fallback_model}")
                print(f"   Reason: {fallback_info['description']}")
                
                return True, 'reference_image', fallback_model, mapped_kwargs
    
    # 检查parameter invalidation条件
    if 'parameter_invalidation' in fallback_config:
        model_config = REPLICATE_MODELS.get(model_name, {})
        supported_params = model_config.get('supported_params', {})
        
        # 检查是否有不支持的参数
        unsupported_params = []
        for param_name in kwargs:
            if param_name not in supported_params and param_name != 'output_filepath':
                unsupported_params.append(param_name)
        
        if unsupported_params:
            fallback_info = fallback_config['parameter_invalidation']
            fallback_model = fallback_info['fallback_model']
            mapped_kwargs = map_parameters(model_name, fallback_model, kwargs)
            
            print(f"🔄 Unsupported parameters detected: {unsupported_params}")
            print(f"   Falling back from {model_name} to {fallback_model}")
            print(f"   Reason: {fallback_info['description']}")
            
            return True, 'parameter_invalidation', fallback_model, mapped_kwargs
    
    return False, None, None, kwargs

def map_parameters(source_model, target_model, kwargs):
    """将参数从源模型映射到目标模型
    
    Args:
        source_model: 源模型名称
        target_model: 目标模型名称  
        kwargs: 原始参数字典
        
    Returns:
        dict: 映射后的参数字典
    """
    mapping_key = (source_model, target_model)
    mapping_config = FALLBACK_PARAMETER_MAPPING.get(mapping_key, {})
    
    if not mapping_config:
        print(f"⚠️  No parameter mapping found for {source_model} -> {target_model}")
        return kwargs
    
    mapped_kwargs = {}
    
    # 1. 直接映射参数
    param_mapping = mapping_config.get('param_mapping', {})
    for source_param, target_param in param_mapping.items():
        if source_param in kwargs:
            value = kwargs[source_param]
            
            # 检查是否需要值映射
            value_mapping = mapping_config.get('value_mapping', {}).get(source_param, {})
            if value_mapping and value in value_mapping:
                value = value_mapping[value]
                print(f"   📝 Mapped {source_param}={kwargs[source_param]} -> {target_param}={value}")
            else:
                print(f"   ✅ Mapped {source_param} -> {target_param}")
            
            mapped_kwargs[target_param] = value
    
    # 2. 添加未映射但目标模型支持的参数
    remove_params = set(mapping_config.get('remove_params', []))
    for param_name, param_value in kwargs.items():
        if (param_name not in param_mapping and 
            param_name not in remove_params and
            param_name != 'output_filepath'):  # 保留output_filepath
            # 检查目标模型是否支持这个参数
            target_model_config = REPLICATE_MODELS.get(target_model, {})
            target_supported_params = target_model_config.get('supported_params', {})
            
            if param_name in target_supported_params:
                mapped_kwargs[param_name] = param_value
                print(f"   ➡️  Kept {param_name} (supported by target model)")
    
    # 3. 添加默认参数
    add_params = mapping_config.get('add_params', {})
    for param_name, param_value in add_params.items():
        if param_name not in mapped_kwargs:  # 不覆盖已有参数
            mapped_kwargs[param_name] = param_value
            print(f"   ➕ Added {param_name}={param_value}")
    
    # 4. 保留output_filepath
    if 'output_filepath' in kwargs:
        mapped_kwargs['output_filepath'] = kwargs['output_filepath']
    
    # 5. 显示移除的参数
    removed_params = [p for p in kwargs if p not in mapped_kwargs and p != 'output_filepath']
    if removed_params:
        print(f"   ❌ Removed unsupported params: {removed_params}")
    
    return mapped_kwargs

def execute_fallback_on_error(original_model, error, **kwargs):
    """在API调用失败时执行fallback
    
    Args:
        original_model: 原始模型名称
        error: 错误信息
        **kwargs: 原始参数
        
    Returns:
        tuple: (should_fallback, fallback_model, mapped_kwargs)
    """
    fallback_config = FALLBACK_MODELS.get(original_model, {})
    
    if 'fail' in fallback_config:
        fallback_info = fallback_config['fail']
        fallback_model = fallback_info['fallback_model']
        mapped_kwargs = map_parameters(original_model, fallback_model, kwargs)
        
        print(f"❌ {original_model} failed with error: {str(error)}")
        print(f"🔄 Falling back to {fallback_model}")
        print(f"   Reason: {fallback_info['description']}")
        
        return True, fallback_model, mapped_kwargs
    
    print(f"❌ {original_model} failed and no fallback available")
    return False, None, kwargs

def replicate_model_calling(prompt, model_name, **kwargs):
    """
    智能模型调用函数，支持自动Fallback机制
    
    Args:
        prompt: 生成提示词
        model_name: 模型名称
        **kwargs: 模型参数
        
    Returns:
        list: 生成文件的路径列表
    """
    os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")
    output_filepath = kwargs.get("output_filepath", os.path.join("output", f"output_{model_name}.jpg"))
    
    original_model = model_name
    current_kwargs = kwargs.copy()
    fallback_chain = []  # 记录fallback链
    
    print(f"🚀 Starting generation with {model_name}")
    
    # 第一步：检查是否需要预处理fallback（reference image, parameter invalidation）
    should_fallback, fallback_reason, fallback_model, mapped_kwargs = check_fallback_conditions(model_name, **current_kwargs)
    
    if should_fallback:
        fallback_chain.append(f"{model_name} -> {fallback_model} ({fallback_reason})")
        model_name = fallback_model
        current_kwargs = mapped_kwargs
        print(f"🔄 Pre-processing fallback applied: {model_name}")
    
    # 尝试调用模型，支持失败后的fallback
    max_fallback_attempts = 3  # 最多尝试3次fallback
    attempt = 0
    
    while attempt <= max_fallback_attempts:
        try:
            print(f"📞 Attempting call to {model_name} (attempt {attempt + 1})")
            
            # Build input parameters based on model configuration and user kwargs
            input_params = {"prompt": prompt}
            
            # Get model configuration
            model_config = REPLICATE_MODELS.get(model_name, {})
            supported_params = model_config.get('supported_params', {})
            
            # Add parameters from kwargs that are supported by the model
            for param_name, param_config in supported_params.items():
                if param_name in current_kwargs:
                    # Handle file inputs specially
                    if param_config.get('type') == 'file' and current_kwargs[param_name] is not None:
                        file_input = current_kwargs[param_name]
                        # If it's a string, treat as file path or URL
                        if isinstance(file_input, str):
                            # Check if it's a URL
                            if file_input.startswith(('http://', 'https://')):
                                input_params[param_name] = file_input
                            else:
                                # Treat as local file path, open it
                                try:
                                    input_params[param_name] = open(file_input, 'rb')
                                    print(f"📁 Opened file: {file_input}")
                                except FileNotFoundError:
                                    print(f"⚠️  File not found: {file_input}, skipping parameter {param_name}")
                                    continue
                        else:
                            # Already a file object or other acceptable format
                            input_params[param_name] = file_input
                    else:
                        input_params[param_name] = current_kwargs[param_name]
                elif param_config['default'] is not None:
                    input_params[param_name] = param_config['default']
            
            print(f"📋 Final parameters for {model_name}: {input_params}")
            
            # 实际调用Replicate API
            output = replicate.run(model_name, input=input_params)
            
            len_output = len(output)
            print(f"✅ {model_name} succeeded! Processing {len_output} file(s)")
            
            # 处理输出文件
            saved_files = []
            for index, item in enumerate(output):
                base_name, ext = os.path.splitext(output_filepath)
                if len_output > 1: 
                    current_filepath = f"{base_name}_{index+1}{ext}"
                else: 
                    current_filepath = output_filepath
                
                with open(current_filepath, "wb") as file: 
                    file.write(item.read())
                saved_files.append(current_filepath)
            
            # 显示fallback链信息
            if fallback_chain:
                print(f"🔗 Fallback chain: {' -> '.join(fallback_chain)} -> SUCCESS")
                print(f"   Original model: {original_model}")
                print(f"   Final model: {model_name}")
            
            return saved_files if saved_files else [output_filepath]
            
        except Exception as error:
            attempt += 1
            
            # 如果已经是最后一次尝试，抛出错误
            if attempt > max_fallback_attempts:
                print(f"❌ All fallback attempts exhausted. Final error: {str(error)}")
                if fallback_chain:
                    print(f"🔗 Attempted fallback chain: {' -> '.join(fallback_chain)} -> FAILED")
                raise error
            
            # 尝试执行失败后的fallback
            should_fallback, fallback_model, mapped_kwargs = execute_fallback_on_error(model_name, error, **current_kwargs)
            
            if should_fallback:
                fallback_chain.append(f"{model_name} -> {fallback_model} (api_error)")
                model_name = fallback_model
                current_kwargs = mapped_kwargs
                print(f"🔄 Error fallback applied: {model_name}")
            else:
                print(f"❌ No fallback available for {model_name}")
                if fallback_chain:
                    print(f"🔗 Partial fallback chain: {' -> '.join(fallback_chain)} -> FAILED")
                raise error

if __name__ == "__main__":
    model_list = list(REPLICATE_MODELS.keys())   
    option_list = [f"{str(index + 1)}: {model_list[index]}" for index in range(len(model_list))] 
    option_list.append("p: View all model parameters")
    option_list_string = "\n".join(option_list)
    
    while True:
        prompt = input("Enter a prompt: ")
        
        optimize = input("Do you want to optimize the prompt with Gemini? (y/n): ").lower().strip()
        if optimize in ['y', 'yes']:
            optimized_prompt = optimize_prompt_with_gemini(prompt)
            if optimized_prompt:
                use_optimized = input("Use optimized prompt? (y/n): ").lower().strip()
                if use_optimized in ['y', 'yes']:
                    prompt = optimized_prompt
        
        choose_model = input(f"Choose a model: \n{option_list_string}\n")
        
        # Check if user wants to view parameters first
        if choose_model.lower() in ['p', 'params', 'parameters']:
            print("\n=== ALL MODELS PARAMETERS ===")
            view_specific = input("View specific model parameters? Enter model number or 'all' for all models: ").strip()
            
            if view_specific.lower() == 'all':
                for i, model_name in enumerate(model_list):
                    print(f"\n{i+1}. {get_supported_parameters(model_name, format_for_display=True)}")
            elif view_specific.isdigit() and 1 <= int(view_specific) <= len(model_list):
                model_to_view = model_list[int(view_specific) - 1]
                print(get_supported_parameters(model_to_view, format_for_display=True))
            else:
                print("Invalid selection")
            
            # Ask again for model choice
            choose_model = input(f"Choose a model: \n{option_list_string}\n")
        
        selected_model = model_list[int(choose_model) - 1]
        
        # Show parameters for selected model
        view_params = input(f"\nView parameters for {selected_model}? (y/n): ").lower().strip()
        if view_params in ['y', 'yes']:
            print(get_supported_parameters(selected_model, format_for_display=True))
        
        # Check if model supports reference image
        custom_params = {}
        if supports_reference_image(selected_model):
            image_param_name = get_image_input_param_name(selected_model)
            if image_param_name:
                use_reference = input(f"\nThis model supports reference images via '{image_param_name}'. Add reference image? (y/n): ").lower().strip()
                if use_reference in ['y', 'yes']:
                    image_input = input("Enter image file path or URL: ").strip()
                    if image_input:
                        custom_params[image_param_name] = image_input
                        print(f"Will use {image_input} as {image_param_name}")
        
        # Allow user to customize other parameters
        customize_params = input("\nCustomize other parameters? (y/n): ").lower().strip()
        if customize_params in ['y', 'yes']:
            model_config = REPLICATE_MODELS.get(selected_model, {})
            supported_params = model_config.get('supported_params', {})
            
            if supported_params:
                print(f"\nAvailable parameters for {selected_model}:")
                for param_name, param_config in supported_params.items():
                    if param_config.get('type') == 'file':
                        continue  # Skip file parameters (already handled)
                    
                    current_default = param_config.get('default', 'None')
                    param_type = param_config.get('type', 'unknown')
                    
                    # Show parameter info
                    print(f"\n• {param_name} ({param_type}, default: {current_default})")
                    if 'options' in param_config:
                        print(f"  Options: {param_config['options']}")
                    if 'range' in param_config:
                        print(f"  Range: {param_config['range']}")
                    if 'description' in param_config:
                        print(f"  Description: {param_config['description']}")
                    
                    # Get user input
                    user_input = input(f"  Enter value for {param_name} (press Enter to use default): ").strip()
                    
                    if user_input:
                        # Convert to appropriate type
                        try:
                            if param_type == 'int':
                                custom_params[param_name] = int(user_input)
                            elif param_type == 'float':
                                custom_params[param_name] = float(user_input)
                            elif param_type == 'bool':
                                custom_params[param_name] = user_input.lower() in ['true', '1', 'yes', 'y']
                            else:
                                custom_params[param_name] = user_input
                            print(f"  ✅ Set {param_name} = {custom_params[param_name]}")
                        except ValueError:
                            print(f"  ❌ Invalid value for {param_name}, using default")
                
                if custom_params:
                    print(f"\nFinal custom parameters: {json.dumps(custom_params, indent=2)}")
            else:
                print("No customizable parameters available for this model")
        
        starting_time = time.time()
        output_filepaths = replicate_model_calling(
            prompt, 
            selected_model, 
            output_filepath=os.path.join("output", f"{str(int(starting_time))}.jpg"),
            **custom_params
        )
        finish_time = time.time()
        process_duration = finish_time - starting_time
        print(f"Process duration: {process_duration}")
        
        # Rename all generated files with model name and duration
        model_name = model_list[int(choose_model) - 1].replace("/", "_").replace("-", "_")
        final_filepaths = []
        
        for i, filepath in enumerate(output_filepaths):
            base_name, ext = os.path.splitext(filepath)
            if len(output_filepaths) > 1: new_filepath = os.path.join("output", f"{model_name}_{int(finish_time)}_{str(int(process_duration))}s_{i+1}{ext}")
            else: new_filepath = os.path.join("output", f"{model_name}_{int(finish_time)}_{str(int(process_duration))}s{ext}")
            
            os.rename(filepath, new_filepath)
            final_filepaths.append(new_filepath)
        
        print(f"Generated {len(final_filepaths)} file(s):")
        for filepath in final_filepaths: print(f"  - {filepath}")


def main():
    """Command line interface for replicate model calling"""
    import argparse
    parser = argparse.ArgumentParser(description='Replicate Batch Process')
    parser.add_argument('--prompt', required=True, help='Text prompt for generation')
    parser.add_argument('--model', default='black-forest-labs/flux-dev', help='Model name')
    parser.add_argument('--output', help='Output file path')
    
    args = parser.parse_args()
    
    result = replicate_model_calling(
        prompt=args.prompt,
        model_name=args.model,
        output_filepath=args.output
    )
    
    print(f"Generated: {result}")


if __name__ == "__main__":
    main()
        