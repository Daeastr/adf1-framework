#!/usr/bin/env python3
"""
Dry run script to test translation actions without external dependencies.
"""

from core.orchestrator import call_action, create_context

def main():
    """Run translation workflow tests."""
    print("=== Translation Actions Dry Run ===\n")
    
    # Create context for maintaining state
    context = create_context()
    
    # Test 1: Initialize translation system
    print("1. Initializing translation system...")
    result = call_action("translation_init", context)
    print(f"   Result: {result}\n")
    
    # Test 2: Set translation languages
    print("2. Setting translation languages...")
    result = call_action("set_translation_languages", context, source_lang="en", target_lang="es")
    print(f"   Result: {result}\n")
    
    # Test 3: Get supported languages
    print("3. Getting supported languages...")
    result = call_action("get_supported_languages", context)
    print(f"   Result: {result}\n")
    
    # Test 4: Detect language
    print("4. Detecting language of text...")
    test_text = "Hello, how are you today?"
    result = call_action("detect_language", context, test_text)
    print(f"   Text: '{test_text}'")
    print(f"   Result: {result}\n")
    
    # Test 5: Translate single text
    print("5. Translating single text...")
    result = call_action("translate_text", context, test_text)
    print(f"   Original: '{test_text}'")
    print(f"   Result: {result}\n")
    
    # Test 6: Batch translation
    print("6. Batch translating multiple texts...")
    test_texts = [
        "Good morning!",
        "How are you?", 
        "Thank you very much.",
        "See you later!"
    ]
    result = call_action("translation_batch", context, test_texts)
    print(f"   Original texts: {test_texts}")
    print(f"   Result: {result}\n")
    
    # Test 7: Change target language and translate
    print("7. Changing target language to French...")
    call_action("set_translation_languages", context, target_lang="fr")
    result = call_action("translate_text", context, "Good evening!", source_lang="en")
    print(f"   Result: {result}\n")
    
    # Test 8: Cleanup
    print("8. Cleaning up translation resources...")
    result = call_action("translation_cleanup", context)
    print(f"   Result: {result}\n")
    
    print("=== Dry Run Complete ===")

def test_error_handling():
    """Test error handling for invalid actions."""
    print("\n=== Error Handling Tests ===\n")
    
    context = create_context()
    
    # Test invalid action name
    try:
        call_action("nonexistent_action", context)
    except ValueError as e:
        print(f"✓ Correctly caught error for invalid action: {e}")
    
    # Test translation without setting languages
    try:
        result = call_action("translate_text", context, "Hello")
        print(f"✓ Translation without languages handled: {result}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

if __name__ == "__main__":
    main()
    test_error_handling()