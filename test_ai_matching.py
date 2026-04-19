"""
Test script for AI-powered organ matching endpoint
Tests the /ai/match_analysis endpoint with actual Gemini API calls
"""

import requests
import json
from datetime import datetime
import sys

# Configuration
BASE_URL = 'http://localhost:5000'
TEST_TIMEOUT = 30

class TestAIMatching:
    def __init__(self):
        self.session = requests.Session()
        self.results = []
        self.passed = 0
        self.failed = 0
        self.hospital_id = None
        self.donor_id = None
        self.recipient_id = None
    
    def login_admin(self):
        """Login as admin to access routes"""
        print("\n📋 [1/5] Testing Admin Login...")
        try:
            response = self.session.post(
                f'{BASE_URL}/admin/login',
                data={'username': 'admin', 'password': 'admin123'},
                allow_redirects=False
            )
            if response.status_code in [200, 302]:
                print("✅ Admin login successful")
                self.passed += 1
                return True
            else:
                print(f"❌ Admin login failed: {response.status_code}")
                self.failed += 1
                return False
        except Exception as e:
            print(f"❌ Admin login error: {e}")
            self.failed += 1
            return False
    
    def login_hospital(self):
        """Login as hospital to get hospital_id in session"""
        print("\n🏥 [2/5] Testing Hospital Login...")
        try:
            # First create/login with a hospital
            response = self.session.post(
                f'{BASE_URL}/login',
                data={
                    'email': 'test@neurobridge.com',
                    'password': 'test123'
                },
                allow_redirects=False,
                timeout=TEST_TIMEOUT
            )
            
            # If login fails, the database may not have test data
            # Check if hospital_id is in session cookies
            if 'hospital_id' in self.session.cookies or response.status_code in [200, 302]:
                print("✅ Hospital login successful")
                self.passed += 1
                return True
            else:
                print(f"⚠️  Hospital login returned: {response.status_code}")
                print("   (May need test data - continuing with direct API test)")
                return True  # Continue anyway for API test
        except Exception as e:
            print(f"⚠️  Hospital login error: {e}")
            print("   (Continuing with direct API test)")
            return True
    
    def create_test_data(self):
        """Create test donor and recipient data"""
        print("\n➕ [3/5] Creating Test Data...")
        try:
            from models import db, Hospital, Donor, Recipient
            from app import app
            
            with app.app_context():
                # Check if test hospital exists
                hospital = Hospital.query.filter_by(email='test@neurobridge.com').first()
                
                if not hospital:
                    hospital = Hospital(
                        name='Test Hospital',
                        email='test@neurobridge.com',
                        password='test123',
                        city='Test City'
                    )
                    db.session.add(hospital)
                    db.session.commit()
                    print(f"   ✓ Created test hospital (ID: {hospital.id})")
                
                self.hospital_id = hospital.id
                
                # Create test donor
                donor = Donor(
                    name='Test Donor',
                    age=45,
                    blood_group='O+',
                    organ='Heart',
                    city='Test City',
                    phone='1234567890',
                    hospital_id=hospital.id
                )
                db.session.add(donor)
                db.session.commit()
                self.donor_id = donor.id
                print(f"   ✓ Created test donor (ID: {donor.id})")
                
                # Create test recipient
                recipient = Recipient(
                    name='Test Recipient',
                    age=40,
                    blood_group='O+',
                    organ='Heart',
                    urgency='High',
                    city='Test City',
                    phone='9876543210',
                    hospital_id=hospital.id
                )
                db.session.add(recipient)
                db.session.commit()
                self.recipient_id = recipient.id
                print(f"   ✓ Created test recipient (ID: {recipient.id})")
                
                print("✅ Test data created successfully")
                self.passed += 1
                return True
        except Exception as e:
            print(f"❌ Test data creation error: {e}")
            self.failed += 1
            return False
    
    def test_ai_matching_endpoint(self):
        """Test the /ai/match_analysis endpoint"""
        print("\n🤖 [4/5] Testing AI Match Analysis Endpoint...")
        
        if not self.donor_id or not self.recipient_id:
            print("❌ Missing test data (donor_id or recipient_id)")
            self.failed += 1
            return False
        
        try:
            payload = {
                'donor_id': self.donor_id,
                'recipient_id': self.recipient_id
            }
            
            print(f"   Sending request with donor_id={self.donor_id}, recipient_id={self.recipient_id}")
            
            response = self.session.post(
                f'{BASE_URL}/ai/match_analysis',
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=TEST_TIMEOUT
            )
            
            print(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response data: {json.dumps(data, indent=2)}")
                
                # Validate response structure
                required_fields = ['compatible', 'score', 'reasons']
                missing_fields = [f for f in required_fields if f not in data]
                
                if missing_fields:
                    print(f"❌ Missing fields in response: {missing_fields}")
                    self.failed += 1
                    return False
                
                # Validate data types
                if not isinstance(data['compatible'], bool):
                    print(f"❌ 'compatible' should be boolean, got {type(data['compatible'])}")
                    self.failed += 1
                    return False
                
                if not isinstance(data['score'], (int, float)) or not (0 <= data['score'] <= 100):
                    print(f"❌ 'score' should be 0-100, got {data['score']}")
                    self.failed += 1
                    return False
                
                if not isinstance(data['reasons'], list):
                    print(f"❌ 'reasons' should be a list, got {type(data['reasons'])}")
                    self.failed += 1
                    return False
                
                print("\n✅ AI Match Analysis Response Valid!")
                print(f"   Compatible: {data['compatible']}")
                print(f"   Score: {data['score']}/100")
                print(f"   Reasons: {data['reasons']}")
                if 'medical_notes' in data:
                    print(f"   Medical Notes: {data['medical_notes']}")
                
                self.passed += 1
                return True
            
            elif response.status_code == 401:
                print(f"❌ Unauthorized (need to login)")
                self.failed += 1
                return False
            
            elif response.status_code == 404:
                print(f"❌ Donor or recipient not found")
                self.failed += 1
                return False
            
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                print(f"   Response: {response.text}")
                self.failed += 1
                return False
        
        except requests.exceptions.Timeout:
            print(f"❌ Request timeout (Gemini API may be slow)")
            self.failed += 1
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            self.failed += 1
            return False
    
    def test_chatbot_endpoint(self):
        """Test the /chat endpoint"""
        print("\n💬 [5/5] Testing Chatbot Endpoint...")
        try:
            payload = {
                'message': 'What is blood type compatibility for organ matching?'
            }
            
            print(f"   Sending: '{payload['message']}'")
            
            response = requests.post(
                f'{BASE_URL}/chat',
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=TEST_TIMEOUT
            )
            
            print(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if 'response' not in data:
                    print(f"❌ Missing 'response' field")
                    self.failed += 1
                    return False
                
                print(f"\n✅ Chatbot Response Valid!")
                print(f"   AI Response: {data['response'][:200]}...")
                print(f"   Has Voice: {data.get('has_voice', False)}")
                print(f"   Model: {data.get('model', 'Unknown')}")
                
                self.passed += 1
                return True
            
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                self.failed += 1
                return False
        
        except requests.exceptions.Timeout:
            print(f"❌ Request timeout")
            self.failed += 1
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            self.failed += 1
            return False
    
    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Success Rate: {(self.passed/total*100):.1f}%" if total > 0 else "N/A")
        print("="*60 + "\n")
        
        return self.failed == 0
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting AI Matching Endpoint Tests...")
        print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Base URL: {BASE_URL}")
        print("="*60)
        
        # Run tests in sequence
        self.login_admin()
        self.login_hospital()
        self.create_test_data()
        self.test_ai_matching_endpoint()
        self.test_chatbot_endpoint()
        
        # Print summary
        success = self.print_summary()
        
        return success

if __name__ == '__main__':
    tester = TestAIMatching()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
