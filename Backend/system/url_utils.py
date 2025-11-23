"""
URL Utilities for eSewa Payment Integration
Handles malformed URLs from eSewa callback redirects
"""


def fix_esewa_callback_url(url):
    """
    Fix malformed eSewa callback URLs where 'data' parameter comes after a second '?'
    
    eSewa sometimes constructs callback URLs incorrectly by appending the 'data'
    parameter with '?' instead of '&', breaking query string parsing:
    
    WRONG:  /verify-and-book/?param1=val1&param2=val2?data=BASE64
    CORRECT: /verify-and-book/?param1=val1&param2=val2&data=BASE64
    
    Args:
        url (str): Full URL string that may contain a second '?' in query string
        
    Returns:
        str: Fixed URL with second '?' replaced by '&'
        
    Examples:
        >>> url = 'http://localhost:8000/api/system/esewa/verify-and-book/?booking_reference=BK123&package_id=8?data=BASE64'
        >>> fix_esewa_callback_url(url)
        'http://localhost:8000/api/system/esewa/verify-and-book/?booking_reference=BK123&package_id=8&data=BASE64'
        
        >>> url = 'http://localhost:8000/api/system/esewa/verify-and-book/?param=value'
        >>> fix_esewa_callback_url(url)
        'http://localhost:8000/api/system/esewa/verify-and-book/?param=value'
        
    Notes:
        - Only replaces the SECOND '?' (first one after initial query start)
        - If URL has only one '?', returns unchanged
        - Safe to call on already-correct URLs
        - Works with full URLs or just query strings
    """
    if not url or not isinstance(url, str):
        return url
    
    # Count question marks in the URL
    question_mark_count = url.count('?')
    
    # If 0 or 1 question marks, URL is fine
    if question_mark_count <= 1:
        return url
    
    # Find the position of the first '?'
    first_q_pos = url.find('?')
    
    # Find the position of the second '?' (search after the first one)
    second_q_pos = url.find('?', first_q_pos + 1)
    
    if second_q_pos == -1:
        # Should not happen if count > 1, but safety check
        return url
    
    # Replace the second '?' with '&'
    fixed_url = url[:second_q_pos] + '&' + url[second_q_pos + 1:]
    
    # If there are more than 2 question marks, recursively fix them
    if question_mark_count > 2:
        return fix_esewa_callback_url(fixed_url)
    
    return fixed_url


def get_query_string_from_url(url):
    """
    Extract query string from URL after fixing malformed URLs
    
    Args:
        url (str): Full URL string
        
    Returns:
        str: Query string portion (everything after '?')
        
    Examples:
        >>> get_query_string_from_url('http://example.com/path?param1=val1&param2=val2')
        'param1=val1&param2=val2'
        
        >>> get_query_string_from_url('http://example.com/path')
        ''
    """
    if not url or '?' not in url:
        return ''
    
    # Fix URL first
    fixed_url = fix_esewa_callback_url(url)
    
    # Extract query string
    return fixed_url.split('?', 1)[1] if '?' in fixed_url else ''


def parse_esewa_query_params(query_string):
    """
    Parse query string into dictionary, handling URL encoding
    
    Args:
        query_string (str): Query string to parse (without leading '?')
        
    Returns:
        dict: Dictionary of parameter name -> value
        
    Examples:
        >>> parse_esewa_query_params('param1=value1&param2=value2')
        {'param1': 'value1', 'param2': 'value2'}
    """
    from urllib.parse import parse_qs, unquote_plus
    
    if not query_string:
        return {}
    
    # Parse query string
    parsed = parse_qs(query_string, keep_blank_values=True)
    
    # Convert lists to single values (DRF style)
    result = {}
    for key, values in parsed.items():
        # Decode URL-encoded keys and values
        decoded_key = unquote_plus(key)
        decoded_value = unquote_plus(values[0]) if values else ''
        result[decoded_key] = decoded_value
    
    return result


# Test cases
if __name__ == '__main__':
    print("="*80)
    print("Testing fix_esewa_callback_url()")
    print("="*80)
    
    test_cases = [
        {
            'name': 'Malformed URL with second ? before data parameter',
            'input': 'http://localhost:8000/api/system/esewa/verify-and-book/?booking_reference=BK123&package_id=8&traveler_address=sdfsdf?data=BASE64DATA',
            'expected': 'http://localhost:8000/api/system/esewa/verify-and-book/?booking_reference=BK123&package_id=8&traveler_address=sdfsdf&data=BASE64DATA'
        },
        {
            'name': 'Already correct URL',
            'input': 'http://localhost:8000/api/system/esewa/verify-and-book/?booking_reference=BK123&package_id=8&data=BASE64',
            'expected': 'http://localhost:8000/api/system/esewa/verify-and-book/?booking_reference=BK123&package_id=8&data=BASE64'
        },
        {
            'name': 'URL with no query string',
            'input': 'http://localhost:8000/api/system/esewa/verify-and-book/',
            'expected': 'http://localhost:8000/api/system/esewa/verify-and-book/'
        },
        {
            'name': 'URL with multiple extra ? marks',
            'input': 'http://localhost:8000/api/system/esewa/verify-and-book/?param1=val1?param2=val2?data=BASE64',
            'expected': 'http://localhost:8000/api/system/esewa/verify-and-book/?param1=val1&param2=val2&data=BASE64'
        },
        {
            'name': 'Relative URL path',
            'input': '/api/system/esewa/verify-and-book/?booking_reference=BK123?data=BASE64',
            'expected': '/api/system/esewa/verify-and-book/?booking_reference=BK123&data=BASE64'
        },
        {
            'name': 'Empty string',
            'input': '',
            'expected': ''
        },
        {
            'name': 'None value',
            'input': None,
            'expected': None
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        result = fix_esewa_callback_url(test['input'])
        is_pass = result == test['expected']
        
        if is_pass:
            passed += 1
            print(f"\n✅ PASS: {test['name']}")
        else:
            failed += 1
            print(f"\n❌ FAIL: {test['name']}")
            print(f"   Input:    {test['input']}")
            print(f"   Expected: {test['expected']}")
            print(f"   Got:      {result}")
    
    print(f"\n{'='*80}")
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("="*80)
    
    # Example usage
    print("\n" + "="*80)
    print("Example Usage")
    print("="*80)
    
    malformed_url = 'http://localhost:8000/api/system/esewa/verify-and-book/?booking_reference=BK80AEBE1D39&package_id=8&payment_amount=1800&traveler_name=Ayush+shahi&traveler_email=ayush.shahi.147%40gmail.com&traveler_phone=9861291159&traveler_address=dafsdf?data=dHJhbnNhY3Rpb25fY29kZT0wMDA3WU1N'
    
    print(f"\nOriginal URL (malformed):")
    print(f"  {malformed_url}")
    
    fixed = fix_esewa_callback_url(malformed_url)
    print(f"\nFixed URL:")
    print(f"  {fixed}")
    
    # Show query string extraction
    query_string = get_query_string_from_url(malformed_url)
    print(f"\nExtracted query string:")
    print(f"  {query_string[:100]}...")
    
    # Show parsed params
    params = parse_esewa_query_params(query_string)
    print(f"\nParsed parameters:")
    for key, value in params.items():
        if key == 'data':
            print(f"  {key}: {value[:50]}... (truncated)")
        else:
            print(f"  {key}: {value}")
