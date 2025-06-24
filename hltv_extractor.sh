#!/bin/bash

# HLTV Demo Link Extractor using curl and bash
# Usage: ./extract_demos.sh

# Configuration
INPUT_FILE="all_match_urls.txt"
OUTPUT_FILE="all_match_download_url.txt"
TEMP_DIR="/tmp/hltv_extract"

# Your cookies (replace with your actual cookies)
COOKIES='MatchFilter={%22active%22:false%2C%22live%22:false%2C%22stars%22:1%2C%22lan%22:false%2C%22teams%22:[]}; CookieConsent={stamp:%27u8L5O1rcViNqYoXcNZ+k+tJTNiNT4E2/gn+7lJv9ePciQR4Q4+Uozg==%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cmethod:%27explicit%27%2Cver:1%2Cutc:1750547842037%2Cregion:%27ca%27}; _fbp=fb.1.1750547842684.762220481359827557; _gcl_au=1.1.1763020324.1750547843; _ga=GA1.1.631546036.1750547843; hb_insticator_uid=b57a7f9c-83d4-436e-a14d-0f3b9c500e6b; _pubcid=e1295c0f-dd25-4d41-acff-e6c8e0999b9c; _pubcid_cst=VyxHLMwsHQ%3D%3D; _lr_env_src_ats=false; _cc_id=82738d3b4bf71237407590e3bfa12082; panoramaId_expiry=1751152909244; panoramaId=8ffd03fe872881c855bbda23a08f185ca02c6142df0f0bde32ed7419ed75e00f; panoramaIdType=panoDevice; cto_bundle=T3hnDV8zbXdDaVk4NDdRQlpldnNUc2dSVSUyQk1yWVQ0amp6ZVFaemoyMXRtRCUyRlhJOVN3RFZzU2dHQldSRTZjb3hBSmxaTW55Qk1ITEJqUENuUSUyRkpZb0ZCTHFHR3N3QW9Udkh1ZnN0R0l5ZWlSSm5sTlJsT1hJaTM3VTlWaGpreVl1JTJCVjNw; 33acrossIdTp=159c%2Fj%2FT3kpVMQ5sN%2BcGGUuCPA%2B%2F4Lo5IVcPxrXlcnM%3D; nightmode=off; __gads=ID=ad87ab95cbb98ad0:T=1750548106:RT=1750715778:S=ALNI_MZ5tiBf7M7sUNqYb4iPl10sssad6A; __gpi=UID=0000110b01617dd0:T=1750548106:RT=1750715778:S=ALNI_MbRnKaEWIAPPUkkW3CVk5DOmAe4xw; __eoi=ID=4486e928a0bcbe2f:T=1750548106:RT=1750715778:S=AA-AfjZHS5E4MLTBARL8XC3kpH6K; _ga_525WEYQTV9=GS2.1.s1750720023$o7$g0$t1750720023$j60$l0$h0; dicbo_id=%7B%22dicbo_fetch%22%3A1750720023846%7D'

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to make HTTP request with proper headers
fetch_page() {
    local url="$1"
    local output_file="$2"
    
    curl -s \
        -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36" \
        -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7" \
        -H "Accept-Language: en-US,en;q=0.9" \
        -H "Accept-Encoding: gzip, deflate, br, zstd" \
        -H "DNT: 1" \
        -H "Connection: keep-alive" \
        -H "Upgrade-Insecure-Requests: 1" \
        -H "Sec-Fetch-Dest: document" \
        -H "Sec-Fetch-Mode: navigate" \
        -H "Sec-Fetch-Site: same-origin" \
        -H "Sec-Fetch-User: ?1" \
        -H "Cache-Control: max-age=0" \
        -H "sec-ch-ua: \"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"" \
        -H "sec-ch-ua-mobile: ?0" \
        -H "sec-ch-ua-platform: \"Windows\"" \
        -H "Referer: https://www.hltv.org/matches" \
        -H "Cookie: $COOKIES" \
        --compressed \
        --max-time 30 \
        -L \
        "$url" -o "$output_file"
}

# Function to extract demo links from HTML content
extract_demo_links() {
    local html_file="$1"
    local temp_links="$2"
    
    if [[ ! -f "$html_file" ]]; then
        print_error "HTML file not found: $html_file"
        return 1
    fi
    
    # Method 1: grep for /download/demo/ patterns
    grep -oE '/download/demo/[0-9]+' "$html_file" >> "$temp_links" 2>/dev/null
    
    # Method 2: Look for data-demo-link attributes
    grep -oE 'data-demo-link="[^"]*"' "$html_file" | \
        sed 's/data-demo-link="//g' | sed 's/"//g' | \
        grep '/download/demo/' >> "$temp_links" 2>/dev/null
    
    # Method 3: Look for href attributes with demo links
    grep -oE 'href="[^"]*download/demo/[0-9]+[^"]*"' "$html_file" | \
        sed 's/href="//g' | sed 's/"//g' >> "$temp_links" 2>/dev/null
    
    # Method 4: Look for onclick attributes with demo links
    grep -oE 'onclick="[^"]*download/demo/[0-9]+[^"]*"' "$html_file" | \
        sed 's/onclick="[^"]*//g' | grep -oE '/download/demo/[0-9]+' >> "$temp_links" 2>/dev/null
    
    # Method 5: Look for demo links in JSON-like structures
    grep -oE '"[^"]*download/demo/[0-9]+[^"]*"' "$html_file" | \
        sed 's/"//g' | grep -oE '/download/demo/[0-9]+' >> "$temp_links" 2>/dev/null
    
    # Method 6: Case insensitive search for demo patterns
    grep -iE 'demo.*[0-9]+' "$html_file" | \
        grep -oE '/download/demo/[0-9]+' >> "$temp_links" 2>/dev/null
    
    # Method 7: Look for any URL-like patterns containing demo
    grep -oE 'https?://[^[:space:]"'\'']*download/demo/[0-9]+[^[:space:]"'\'']*' "$html_file" >> "$temp_links" 2>/dev/null
}

# Function to convert relative URLs to absolute URLs
convert_to_absolute_urls() {
    local input_file="$1"
    local output_file="$2"
    
    # Convert relative URLs to absolute URLs and remove duplicates
    while IFS= read -r line; do
        if [[ "$line" =~ ^/download/demo/ ]]; then
            echo "https://www.hltv.org$line"
        elif [[ "$line" =~ ^https?:// ]]; then
            echo "$line"
        fi
    done < "$input_file" | sort -u > "$output_file"
}

# Function to test HLTV access
test_hltv_access() {
    print_status "Testing HLTV access..."
    
    local test_file="$TEMP_DIR/test.html"
    fetch_page "https://www.hltv.org/matches" "$test_file"
    
    if [[ -f "$test_file" ]] && [[ -s "$test_file" ]]; then
        local content=$(head -n 20 "$test_file" | tr '[:upper:]' '[:lower:]')
        
        if echo "$content" | grep -q "cloudflare.*check"; then
            print_warning "Cloudflare challenge detected - will try to continue anyway"
        elif echo "$content" | grep -q "hltv"; then
            print_success "Successfully accessed HLTV!"
        else
            print_warning "Unexpected page content - will try to continue anyway"
        fi
        
        local file_size=$(wc -c < "$test_file")
        print_status "Response size: $file_size bytes"
    else
        print_warning "Failed to fetch test page - will try to continue anyway"
    fi
    
    rm -f "$test_file" 2>/dev/null
}

# Function to process a single match URL
process_match_url() {
    local match_url="$1"
    local index="$2"
    local total="$3"
    local temp_links="$4"
    
    print_status "Processing $index/$total: $match_url"
    
    local html_file="$TEMP_DIR/match_$index.html"
    
    # Fetch the page
    fetch_page "$match_url" "$html_file"
    
    if [[ ! -f "$html_file" ]] || [[ ! -s "$html_file" ]]; then
        print_warning "Failed to fetch or empty response for: $match_url"
        return 1
    fi
    
    local file_size=$(wc -c < "$html_file")
    print_status "   Response size: $file_size bytes"
    
    # Check for blocking indicators
    if [[ $file_size -lt 1000 ]]; then
        print_warning "   Small response size - might be blocked"
        local first_line=$(head -n 1 "$html_file")
        print_status "   First line: ${first_line:0:100}..."
    fi
    
    # Extract demo links
    local temp_match_links="$TEMP_DIR/match_${index}_links.txt"
    extract_demo_links "$html_file" "$temp_match_links"
    
    if [[ -f "$temp_match_links" ]] && [[ -s "$temp_match_links" ]]; then
        local link_count=$(wc -l < "$temp_match_links")
        print_success "   Found $link_count demo link(s)"
        
        # Show first few links found
        head -n 3 "$temp_match_links" | while IFS= read -r link; do
            if [[ "$link" =~ ^/download/demo/ ]]; then
                print_success "      ✅ https://www.hltv.org$link"
            else
                print_success "      ✅ $link"
            fi
        done
        
        # Append to main temp file
        cat "$temp_match_links" >> "$temp_links"
    else
        print_warning "   No demo links found"
        
        # Diagnostic info
        if grep -qi "demo" "$html_file"; then
            local demo_count=$(grep -ci "demo" "$html_file")
            print_status "   Contains 'demo': $demo_count times"
        fi
        
        if grep -qi "download" "$html_file"; then
            local download_count=$(grep -ci "download" "$html_file")
            print_status "   Contains 'download': $download_count times"
        fi
    fi
    
    # Cleanup
    rm -f "$html_file" "$temp_match_links" 2>/dev/null
    
    # Random delay between requests
    local delay=$(( RANDOM % 4 + 2 ))
    if [[ $index -lt $total ]]; then
        print_status "   Waiting ${delay}s before next request..."
        sleep $delay
    fi
}

# Main function
main() {
    echo "🚀 HLTV Demo Link Extractor (Bash/Curl Version)"
    echo "=============================================================="
    
    # Check dependencies
    if ! command -v curl &> /dev/null; then
        print_error "curl is required but not installed"
        exit 1
    fi
    
    if ! command -v grep &> /dev/null; then
        print_error "grep is required but not installed"
        exit 1
    fi
    
    # Check input file
    if [[ ! -f "$INPUT_FILE" ]]; then
        print_error "Input file '$INPUT_FILE' not found!"
        exit 1
    fi
    
    # Create temp directory
    mkdir -p "$TEMP_DIR"
    
    # Test HLTV access
    test_hltv_access
    
    # Read match URLs
    print_status "Reading match URLs from '$INPUT_FILE'..."
    mapfile -t match_urls < "$INPUT_FILE"
    
    # Remove empty lines
    match_urls=("${match_urls[@]//[[:space:]]/}")
    match_urls=("${match_urls[@]/#[[:space:]]*/}")
    match_urls=("${match_urls[@]/%[[:space:]]*/}")
    match_urls=("${match_urls[@]//[[:space:]]*}")
    
    # Filter out empty elements
    local filtered_urls=()
    for url in "${match_urls[@]}"; do
        if [[ -n "$url" ]]; then
            filtered_urls+=("$url")
        fi
    done
    match_urls=("${filtered_urls[@]}")
    
    local total_urls=${#match_urls[@]}
    print_status "Found $total_urls match URLs to process"
    
    if [[ $total_urls -eq 0 ]]; then
        print_error "No valid URLs found in input file"
        exit 1
    fi
    
    # Process each URL
    echo
    echo "=============================================================="
    print_status "Processing match URLs..."
    
    local temp_all_links="$TEMP_DIR/all_links.txt"
    > "$temp_all_links"  # Create empty file
    
    for i in "${!match_urls[@]}"; do
        local index=$((i + 1))
        process_match_url "${match_urls[i]}" "$index" "$total_urls" "$temp_all_links"
    done
    
    # Process results
    echo
    echo "=============================================================="
    print_status "Processing results..."
    
    if [[ -f "$temp_all_links" ]] && [[ -s "$temp_all_links" ]]; then
        local temp_absolute="$TEMP_DIR/absolute_links.txt"
        convert_to_absolute_urls "$temp_all_links" "$temp_absolute"
        
        local total_links=$(wc -l < "$temp_all_links" 2>/dev/null || echo 0)
        local unique_links=$(wc -l < "$temp_absolute" 2>/dev/null || echo 0)
        
        print_status "Summary:"
        print_status "   - Processed: $total_urls match URLs"
        print_status "   - Found: $total_links total demo links"
        print_status "   - Unique: $unique_links demo links"
        
        # Save results
        cp "$temp_absolute" "$OUTPUT_FILE"
        print_success "Saved $unique_links unique demo links to '$OUTPUT_FILE'"
        
        if [[ $unique_links -gt 0 ]]; then
            echo
            print_status "Sample demo links found:"
            head -n 5 "$OUTPUT_FILE" | while IFS= read -r link; do
                echo "   🎯 $link"
            done
            
            if [[ $unique_links -gt 5 ]]; then
                print_status "   ... and $((unique_links - 5)) more"
            fi
        fi
    else
        print_warning "No demo links found in any of the processed URLs"
        touch "$OUTPUT_FILE"
    fi
    
    # Cleanup
    rm -rf "$TEMP_DIR" 2>/dev/null
    
    echo
    print_success "🎉 Demo link extraction completed!"
    print_status "📂 Check '$OUTPUT_FILE' for the extracted demo download URLs"
}

# Run main function
main "$@"