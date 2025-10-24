"""
Forward Test DEMO - Shows what will happen right now
Simulates a complete trade cycle immediately for demonstration
"""
from forward_test import ForwardTest
import time

class ForwardTestDemo(ForwardTest):
    """Demo version that runs immediately"""
    
    def run_demo(self):
        """Run demo - enter immediately, monitor for 2 minutes, then exit"""
        print("\n" + "="*80)
        print("🎬 DEMO MODE - Simulating a complete trade cycle NOW")
        print("="*80)
        print("This will:")
        print("  1. Enter positions NOW (instead of waiting for 4:00 PM)")
        print("  2. Monitor for 2 minutes")
        print("  3. Exit and show final P&L")
        print("="*80)
        
        input("\nPress Enter to start demo...")
        
        # Step 1: Enter positions
        if not self.enter_positions():
            print("Failed to enter positions")
            return
        
        # Step 2: Monitor for 2 minutes
        print("\n⏰ Monitoring positions for 2 minutes...")
        print("(Checking every 10 seconds)")
        
        for i in range(12):  # 12 * 10 seconds = 2 minutes
            if not self.positions['call'] and not self.positions['put']:
                print("\n✅ Both positions closed by SL/TP")
                break
            
            time.sleep(10)
            self.monitor_positions()
        
        # Step 3: Exit remaining positions
        if self.positions['call'] or self.positions['put']:
            print("\n⏰ Demo time completed - exiting remaining positions...")
            self.exit_positions()
        
        print("\n" + "="*80)
        print("✅ DEMO COMPLETED")
        print("="*80)
        print("\nThis is how the bot would work in real-time.")
        print("In production, it would:")
        print("  • Wait until 4:00 PM to enter")
        print("  • Monitor continuously until 5:25 PM")
        print("  • Close all positions at 5:25 PM")
        print("="*80)

if __name__ == "__main__":
    print("\n" + "="*80)
    print("📊 FORWARD TEST DEMO")
    print("="*80)
    print("\nThis demo will show you EXACTLY how the bot works by:")
    print("  • Getting live market data RIGHT NOW")
    print("  • Finding ATM and 1 OTM strikes")
    print("  • Showing entry premiums and SL/TP levels")
    print("  • Monitoring for 2 minutes")
    print("  • Showing final P&L")
    print("\n⚠️  NO REAL ORDERS - This is a simulation with live data")
    print("="*80)
    
    demo = ForwardTestDemo()
    demo.run_demo()
