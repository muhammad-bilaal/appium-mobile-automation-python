#!/usr/bin/env python3
"""
Simple Slack Reporter - Creates test results and sends to Slack
"""

import os
import sys
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def read_junit_xml_results():
    """Read JUnit XML results and convert to JSON format"""
    try:
        import xml.etree.ElementTree as ET
        
        tree = ET.parse("test_results.xml")
        root = tree.getroot()
        
        # Find testsuite element (could be nested under testsuites)
        testsuite = root.find("testsuite")
        if testsuite is None:
            testsuite = root  # In case root is testsuite
        
        # Extract test counts from testsuite
        total = int(testsuite.get("tests", 0))
        failures = int(testsuite.get("failures", 0))
        errors = int(testsuite.get("errors", 0))
        skipped = int(testsuite.get("skipped", 0))
        passed = total - failures - errors - skipped
        
        # Extract individual test cases
        tests = []
        for testcase in testsuite.findall("testcase"):
            name = testcase.get("name", "unknown")
            
            # Determine status
            if testcase.find("failure") is not None:
                status = "failed"
            elif testcase.find("error") is not None:
                status = "failed"
            elif testcase.find("skipped") is not None:
                status = "skipped"
            else:
                status = "passed"
            
            tests.append({
                "name": name,
                "status": status
            })
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "total": total,
            "passed": passed,
            "failed": failures + errors,
            "skipped": skipped,
            "tests": tests
        }
        
        # Save as JSON for future reference
        with open("test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"✅ Loaded {results['total']} tests from XML results")
        return results
        
    except FileNotFoundError:
        print("❌ test_results.xml not found. Run your tests first!")
        return None
    except Exception as e:
        print(f"❌ Error reading XML results: {e}")
        return None

def print_results_locally(results):
    """Print results locally when Slack is not available"""
    total = results["total"]
    passed = results["passed"] 
    failed = results["failed"]
    skipped = results["skipped"]
    success_rate = round((passed / total * 100), 2) if total > 0 else 0
    
    print(f"""
🤖 Test Results Report

📊 Summary:
Total: {total} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}
Success Rate: {success_rate}%

📝 Tests:""")
    
    for i, test in enumerate(results["tests"], 1):
        name = test["name"].replace("test_", "").replace("_", " ").title()
        status = test["status"]
        if status == "passed":
            emoji = "✅"
        elif status == "failed":
            emoji = "❌"
        else:
            emoji = "⏭️"
        print(f"{i}. {name} - {emoji}")

def upload_allure_report_to_slack(bot_token, channel_id):
    """Upload Allure HTML report to Slack using modern files.uploadV2 API"""
    allure_files = [
        "allure-report-single.html",        # Single file report from CI
        "reports/allure-report/index.html", # Local test execution path
        "allure-report/index.html",         # Standard report
        "reports/index.html"                # Alternative location
    ]
    
    # Find the Allure report file
    report_file = None
    for file_path in allure_files:
        if os.path.exists(file_path):
            report_file = file_path
            break
    
    if not report_file:
        print("⚠️ No Allure HTML report found to upload")
        return False
    
    try:
        # Step 1: Get upload URL
        filename = f'allure-report-{datetime.now().strftime("%Y%m%d-%H%M%S")}.html'
        
        # Get file size
        file_size = os.path.getsize(report_file)
        
        upload_url_response = requests.post(
            'https://slack.com/api/files.getUploadURLExternal',
            headers={'Authorization': f'Bearer {bot_token}'},
            data={
                'filename': filename,
                'length': file_size
            },
            timeout=30
        )
        
        if not upload_url_response.json().get('ok'):
            error = upload_url_response.json().get('error', 'Unknown error')
            if error == 'missing_scope':
                print("⚠️ Slack bot missing 'files:write' permission - skipping file upload")
                print("💡 Add 'files:write' scope to your Slack bot to enable file uploads")
            elif error == 'not_in_channel':
                print("⚠️ Slack bot not added to the channel - skipping file upload")
                print(f"💡 Add your bot to channel {channel_id} or use a DM (@your_bot_name)")
            else:
                print(f"❌ Failed to get upload URL: {error}")
            return False
        
        upload_url = upload_url_response.json()['upload_url']
        file_id = upload_url_response.json()['file_id']
        
        # Step 2: Upload file to the URL
        with open(report_file, 'rb') as file:
            upload_response = requests.post(
                upload_url,
                files={'file': file},
                timeout=60
            )
        
        if upload_response.status_code != 200:
            print(f"❌ Failed to upload file: HTTP {upload_response.status_code}")
            return False
        
        # Step 3: Complete the upload and share to channel
        complete_response = requests.post(
            'https://slack.com/api/files.completeUploadExternal',
            headers={'Authorization': f'Bearer {bot_token}'},
            json={
                'files': [{
                    'id': file_id,
                    'title': 'Allure Test Report'
                }],
                'channel_id': channel_id.replace('#', ''),
                'initial_comment': '📊 Detailed Allure Test Report - Click to download and open in browser'
            },
            timeout=30
        )
        
        if complete_response.json().get('ok'):
            print("✅ Allure report uploaded to Slack!")
            return True
        else:
            error = complete_response.json().get('error', 'Unknown error')
            if error == 'not_in_channel':
                print("⚠️ Slack bot not added to the channel - skipping file upload")
                print(f"💡 Add your bot to channel {channel_id} or use a DM (@your_bot_name)")
            else:
                print(f"❌ Failed to complete upload: {error}")
            return False
                
    except Exception as e:
        print(f"❌ Error uploading Allure report: {e}")
        return False

def send_to_slack(results):
    """Send results to Slack using Bot Token"""
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    channel_id = os.getenv("SLACK_CHANNEL_ID", "#general")  # Default to #general
    
    if not bot_token:
        print("❌ SLACK_BOT_TOKEN not set - showing results locally instead:")
        print_results_locally(results)
        return False
    
    total = results["total"]
    passed = results["passed"] 
    failed = results["failed"]
    skipped = results["skipped"]
    success_rate = round((passed / total * 100), 2) if total > 0 else 0
    
    message = f"""🤖 Test Results Report

📊 Summary:
Total: {total} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}
Success Rate: {success_rate}%

📝 Tests:"""
    
    for i, test in enumerate(results["tests"], 1):
        name = test["name"].replace("test_", "").replace("_", " ").title()
        status = test["status"]
        if status == "passed":
            emoji = "✅"
        elif status == "failed":
            emoji = "❌"
        else:
            emoji = "⏭️"
        message += f"\n{i}. {name} - {emoji}"
    
    payload = {
        "channel": channel_id,
        "text": message
    }
    
    headers = {
        "Authorization": f"Bearer {bot_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("ok"):
            print("✅ Sent to Slack!")
            return True
        else:
            print(f"❌ Slack API error: {result.get('error', 'Unknown error')}")
            return False
    else:
        print(f"❌ HTTP error: {response.status_code}")
        return False

def main():
    print("🚀 Simple Slack Reporter")
    
    # Read pytest XML results automatically
    results = read_junit_xml_results()
    if not results:
        return 1
    
    print(f"📊 Found {results['total']} tests")
    
    # Send to Slack
    success = send_to_slack(results)
    
    # Also upload Allure report if available
    if success:
        bot_token = os.getenv("SLACK_BOT_TOKEN")
        channel_id = os.getenv("SLACK_CHANNEL_ID", "#general")
        upload_allure_report_to_slack(bot_token, channel_id)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
