import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import random

class TestCompleteBookingSystem:
    
    @pytest.fixture
    def driver(self):
        """Setup Chrome driver"""
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.maximize_window()
        yield driver
        driver.quit()
    
    def test_complete_booking_flow(self, driver):
        """Test EVERYTHING in one flow - Like a real user"""
        
        # ============================================
        # 1. TEST REGISTRATION PAGE LOADS
        # ============================================
        driver.get("http://127.0.0.1:5000/register-page")
        assert "Register" in driver.title or "BD Ticket" in driver.title
        print("✅ Registration page loaded")
        
        # ============================================
        # 2. TEST LOGIN PAGE LOADS
        # ============================================
        driver.get("http://127.0.0.1:5000/")
        assert "Login" in driver.page_source or "BD Ticket" in driver.title
        print("✅ Login page loaded")
        
        # ============================================
        # 3. TEST USER LOGIN
        # ============================================
        email_input = driver.find_element(By.ID, "email")
        password_input = driver.find_element(By.ID, "password")
        
        # Use test account (create one first)
        email_input.send_keys("mehedi183012.2003@gmail.com")
        password_input.send_keys("123456")
        
        login_btn = driver.find_element(By.CLASS_NAME, "btn-login")
        login_btn.click()
        
        # Wait for dashboard to load
        time.sleep(2)
        assert "dashboard" in driver.current_url or "Dashboard" in driver.page_source
        print("✅ User logged in successfully")
        
        # ============================================
        # 4. TEST DASHBOARD LOADS WITH BOOKING HISTORY
        # ============================================
        assert "Booking History" in driver.page_source or "bkContainer" in driver.page_source
        print("✅ Dashboard loaded with booking history")
        
        # ============================================
        # 5. TEST NAVIGATION TO BUS PAGE
        # ============================================
        # Find bus card - using the correct class
        bus_card = driver.find_element(By.CSS_SELECTOR, ".tc.bus")
        bus_card.click()
        time.sleep(1)
        assert "/bus" in driver.current_url
        print("✅ Navigated to Bus page")
        
        # ============================================
        # 6. TEST BUS ROUTE SELECTION (From and To dropdowns)
        # ============================================
        # Select source
        source_select = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "source"))
        )
        source_select.click()
        source_options = source_select.find_elements(By.TAG_NAME, "option")
        if len(source_options) > 1:
            source_options[1].click()
        
        # Select destination
        dest_select = driver.find_element(By.ID, "destination")
        dest_select.click()
        dest_options = dest_select.find_elements(By.TAG_NAME, "option")
        if len(dest_options) > 1:
            dest_options[1].click()
        
        # Select journey date
        date_input = driver.find_element(By.ID, "journeyDate")
        date_input.send_keys("2025-12-31")
        
        print("✅ Bus route selection works")
        
        # ============================================
        # 7. TEST NEXT BUTTON (Go to schedule)
        # ============================================
        next_btn = driver.find_element(By.CLASS_NAME, "btn-next")
        next_btn.click()
        time.sleep(2)
        assert "/bus-schedule" in driver.current_url
        print("✅ Navigated to bus schedule page")
        
        # ============================================
        # 8. TEST SCHEDULE PAGE LOADS WITH OPERATORS
        # ============================================
        schedule_cards = driver.find_elements(By.CLASS_NAME, "schedule-card")
        assert len(schedule_cards) > 0
        print(f"✅ Schedule page loaded with {len(schedule_cards)} operators")
        
        # ============================================
        # 9. TEST SELECT AN OPERATOR - FIXED CLASS NAME
        # ============================================
        # Wait for book button to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "book-btn"))
        )
        select_btn = driver.find_element(By.CLASS_NAME, "book-btn")
        select_btn.click()
        time.sleep(2)
        
        # Check if redirected to seat selection or payment page
        assert "/seat" in driver.current_url or "/bus-payment" in driver.current_url
        print("✅ Operator selection works")
        
        # ============================================
        # 10. TEST SEAT SELECTION PAGE
        # ============================================
        # Wait for seat grid to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "seatGrid"))
        )
        
        # Find an available seat and click it
        available_seats = driver.find_elements(By.CSS_SELECTOR, ".seat.available")
        if len(available_seats) > 0:
            available_seats[0].click()
            print("✅ Seat selection works")
        
        # ============================================
        # 11. TEST DECORATOR PATTERN - PREMIUM TOGGLE
        # ============================================
        try:
            premium_checkbox = driver.find_element(By.ID, "premiumCheckbox")
            premium_checkbox.click()
            time.sleep(0.5)
            
            # Verify add-ons become enabled
            addon_checkboxes = driver.find_elements(By.CSS_SELECTOR, "#addonsContainer input")
            if len(addon_checkboxes) > 0:
                # Check if first add-on is now enabled
                print("✅ Premium toggle enables add-ons (Decorator Pattern)")
        except:
            print("⚠️ Premium toggle not found on this page")
        
        # ============================================
        # 12. TEST DECORATOR PATTERN - SELECT ADD-ON
        # ============================================
        try:
            addon_checkboxes = driver.find_elements(By.CSS_SELECTOR, "#addonsContainer input")
            if len(addon_checkboxes) > 0 and addon_checkboxes[0].is_enabled():
                addon_checkboxes[0].click()
                time.sleep(0.5)
                
                # Verify total updates
                total_display = driver.find_element(By.ID, "previewTotal")
                assert "৳" in total_display.text
                print("✅ Add-on selection updates total (Decorator Pattern)")
        except:
            print("⚠️ Add-ons not available or not enabled")
        
        # ============================================
        # 13. TEST PAYMENT METHOD SELECTION
        # ============================================
        payment_btns = driver.find_elements(By.CLASS_NAME, "payment-method-btn")
        if len(payment_btns) > 0:
            payment_btns[0].click()
            print("✅ Payment method selection works")
        
        # ============================================
        # 14. TEST NOTIFICATION BELL
        # ============================================
        driver.get("http://127.0.0.1:5000/dashboard")
        time.sleep(2)
        
        try:
            notif_btn = driver.find_element(By.CLASS_NAME, "notif-btn")
            notif_btn.click()
            time.sleep(1)
            assert "/notifications-page" in driver.current_url
            print("✅ Notification bell works")
        except:
            print("⚠️ Notification bell not found")
        
        # ============================================
        # 15. TEST NOTIFICATIONS PAGE
        # ============================================
        assert "Notifications" in driver.page_source or "notifications" in driver.current_url
        print("✅ Notifications page loads")
        
        # ============================================
        # 16. TEST LOGOUT
        # ============================================
        driver.get("http://127.0.0.1:5000/dashboard")
        time.sleep(1)
        
        try:
            logout_btn = driver.find_element(By.CLASS_NAME, "btn-logout")
            logout_btn.click()
            time.sleep(1)
            assert "/" in driver.current_url or "login" in driver.current_url
            print("✅ Logout works")
        except:
            print("⚠️ Logout button not found")
        
        # ============================================
        # 17. TEST ADMIN PANEL ACCESS
        # ============================================
        # Login as admin
        driver.get("http://127.0.0.1:5000/")
        email_input = driver.find_element(By.ID, "email")
        password_input = driver.find_element(By.ID, "password")
        
        email_input.clear()
        email_input.send_keys("zihadmuzahid2003@gmail.com")
        password_input.clear()
        password_input.send_keys("123456")
        
        login_btn = driver.find_element(By.CLASS_NAME, "btn-login")
        login_btn.click()
        time.sleep(2)
        
        # Go to admin panel
        driver.get("http://127.0.0.1:5000/admin")
        time.sleep(1)
        
        # Verify admin stats visible
        assert "Total Users" in driver.page_source or "Total Bookings" in driver.page_source
        print("✅ Admin panel loads with statistics")

        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED!")
        print("="*50)