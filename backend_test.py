import requests
import sys
import json
from datetime import datetime

class FinTrackAPITester:
    def __init__(self, base_url="https://spend-income-viz.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            success = response.status_code == expected_status
            
            if success:
                self.log_test(name, True)
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                details = f"Expected {expected_status}, got {response.status_code}. Response: {response.text[:200]}"
                self.log_test(name, False, details)
                return False, {}

        except requests.exceptions.Timeout:
            self.log_test(name, False, "Request timeout")
            return False, {}
        except requests.exceptions.ConnectionError:
            self.log_test(name, False, "Connection error - backend may be down")
            return False, {}
        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test API root endpoint"""
        return self.run_test("API Root", "GET", "", 200)

    def test_get_spendings(self):
        """Test getting all spendings"""
        return self.run_test("Get Spendings", "GET", "spendings", 200)

    def test_get_income(self):
        """Test getting all income records"""
        return self.run_test("Get Income", "GET", "income", 200)

    def test_get_statistics(self):
        """Test getting statistics"""
        return self.run_test("Get Statistics", "GET", "statistics", 200)

    def test_seed_data(self):
        """Test seeding data"""
        return self.run_test("Seed Data", "POST", "seed", 200)

    def test_create_spending(self):
        """Test creating a new spending record"""
        test_spending = {
            "category": "Test Category",
            "date": "2026-01-15",
            "amount": 1000.0
        }
        success, response = self.run_test("Create Spending", "POST", "spendings", 201, test_spending)
        if success and 'id' in response:
            return success, response['id']
        return success, None

    def test_create_income(self):
        """Test creating a new income record"""
        test_income = {
            "month": "2026-02",
            "income": 50000.0,
            "saved": 5000.0,
            "home": 0.0
        }
        return self.run_test("Create Income", "POST", "income", 201, test_income)

    def test_update_spending(self, spending_id):
        """Test updating a spending record"""
        if not spending_id:
            self.log_test("Update Spending", False, "No spending ID available")
            return False, {}
        
        update_data = {
            "amount": 1500.0
        }
        return self.run_test("Update Spending", "PUT", f"spendings/{spending_id}", 200, update_data)

    def test_delete_spending(self, spending_id):
        """Test deleting a spending record"""
        if not spending_id:
            self.log_test("Delete Spending", False, "No spending ID available")
            return False, {}
        
        return self.run_test("Delete Spending", "DELETE", f"spendings/{spending_id}", 200)

    def test_update_income(self):
        """Test updating an income record"""
        update_data = {
            "saved": 10000.0
        }
        return self.run_test("Update Income", "PUT", "income/2026-02", 200, update_data)

    def test_delete_income(self):
        """Test deleting an income record"""
        return self.run_test("Delete Income", "DELETE", "income/2026-02", 200)

    def validate_data_structure(self):
        """Validate the structure of returned data"""
        print("\n📊 Validating Data Structure...")
        
        # Test spendings structure
        success, spendings = self.test_get_spendings()
        if success and isinstance(spendings, list) and len(spendings) > 0:
            spending = spendings[0]
            required_fields = ['id', 'category', 'date', 'amount', 'created_at']
            missing_fields = [field for field in required_fields if field not in spending]
            
            if not missing_fields:
                self.log_test("Spendings Data Structure", True)
            else:
                self.log_test("Spendings Data Structure", False, f"Missing fields: {missing_fields}")
        
        # Test income structure
        success, income = self.test_get_income()
        if success and isinstance(income, list) and len(income) > 0:
            income_record = income[0]
            required_fields = ['id', 'month', 'income', 'saved', 'home', 'created_at']
            missing_fields = [field for field in required_fields if field not in income_record]
            
            if not missing_fields:
                self.log_test("Income Data Structure", True)
            else:
                self.log_test("Income Data Structure", False, f"Missing fields: {missing_fields}")

        # Test statistics structure
        success, stats = self.test_get_statistics()
        if success:
            required_fields = ['total_spending', 'total_income', 'total_saved', 'total_home', 'net_balance']
            missing_fields = [field for field in required_fields if field not in stats]
            
            if not missing_fields:
                self.log_test("Statistics Data Structure", True)
                print(f"   📈 Total Income: {stats.get('total_income', 0):,.0f} IQD")
                print(f"   📉 Total Spending: {stats.get('total_spending', 0):,.0f} IQD")
                print(f"   💰 Net Balance: {stats.get('net_balance', 0):,.0f} IQD")
            else:
                self.log_test("Statistics Data Structure", False, f"Missing fields: {missing_fields}")

def main():
    print("🚀 Starting FinTrack API Testing...")
    print("=" * 50)
    
    tester = FinTrackAPITester()
    
    # Test basic endpoints
    tester.test_root_endpoint()
    tester.test_get_spendings()
    tester.test_get_income()
    tester.test_get_statistics()
    
    # Test data seeding
    tester.test_seed_data()
    
    # Validate data structure
    tester.validate_data_structure()
    
    # Test CRUD operations
    success, spending_id = tester.test_create_spending()
    tester.test_update_spending(spending_id)
    tester.test_delete_spending(spending_id)
    
    tester.test_create_income()
    tester.test_update_income()
    tester.test_delete_income()
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed! Backend API is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the details above.")
        failed_tests = [result for result in tester.test_results if not result['success']]
        print("\nFailed Tests:")
        for test in failed_tests:
            print(f"  - {test['test']}: {test['details']}")
        return 1

if __name__ == "__main__":
    sys.exit(main())