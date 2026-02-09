import datetime
import json
from enum import Enum

class DeviceCategory(Enum):
    """Categories of electronic devices on campus"""
    LAPTOP = "Laptop"
    LAB_EQUIPMENT = "Lab Equipment"
    CONSUMABLE = "Consumable"
    APPLIANCE = "Appliance"
    PERIPHERAL = "Peripheral"

class DisposalStrategy(Enum):
    """Possible end-of-life strategies for devices"""
    RELOCATE = "Relocate to Permanent Campus"
    REPURPOSE = "Repurpose/Upcycle for Labs"
    MARKETPLACE = "Sell on Marketplace"
    STRIP_COMPONENTS = "Strip for Components"
    RECYCLE = "Responsible Recycling"
    HAZARDOUS_DISPOSAL = "Hazardous Material Disposal"

class CampusAsset:
    """Represents a single electronic device or equipment on campus"""
    
    def __init__(self, asset_id, name, model, category, age_years, 
                 battery_health=100, can_refurbish=True, is_hazardous=False):
        self.asset_id = asset_id
        self.name = name
        self.model = model
        self.category = category
        self.age_years = age_years
        self.battery_health = battery_health
        self.can_refurbish = can_refurbish
        self.is_hazardous = is_hazardous
        self.status = "Dormant"
        self.location = "Storage"
        self.last_used = None
        self.disposal_strategy = self.evaluate_disposal_strategy()

    def evaluate_disposal_strategy(self):
        """AI-driven logic to determine the best end-of-life strategy"""
        
        # Hazardous materials need special handling
        if self.is_hazardous:
            return DisposalStrategy.HAZARDOUS_DISPOSAL
        
        # Young devices with good battery health
        if self.age_years < 3 and self.battery_health > 70 and self.can_refurbish:
            return DisposalStrategy.RELOCATE
        
        # Refurbishable devices with moderate age
        elif self.can_refurbish and self.age_years < 5 and self.battery_health > 40:
            return DisposalStrategy.MARKETPLACE
        
        # Lab equipment that can be repurposed
        elif self.category == DeviceCategory.LAB_EQUIPMENT.value and self.can_refurbish:
            return DisposalStrategy.REPURPOSE
        
        # Devices that can be stripped for components
        elif not self.can_refurbish and self.age_years < 7:
            return DisposalStrategy.STRIP_COMPONENTS
        
        # Everything else goes to recycling
        else:
            return DisposalStrategy.RECYCLE

    def update_status(self, new_status):
        """Update the current status of the asset"""
        self.status = new_status
        if new_status == "In Use":
            self.last_used = datetime.datetime.now()

    def to_dict(self):
        """Convert asset to dictionary for storage/display"""
        return {
            'asset_id': self.asset_id,
            'name': self.name,
            'model': self.model,
            'category': self.category,
            'age_years': self.age_years,
            'battery_health': self.battery_health,
            'can_refurbish': self.can_refurbish,
            'is_hazardous': self.is_hazardous,
            'status': self.status,
            'location': self.location,
            'disposal_strategy': self.disposal_strategy.value
        }

    def __str__(self):
        return (f"ID: {self.asset_id} | {self.name} ({self.model}) | "
                f"Category: {self.category} | Age: {self.age_years}yr | "
                f"Battery: {self.battery_health}% | Status: {self.status} | "
                f"Strategy: {self.disposal_strategy.value}")


class CampusInventory:
    """Central inventory management system for all campus assets"""
    
    def __init__(self):
        self.assets = {}
        self.next_id = 1
        self.marketplace_items = []
        self.components_library = []

    def add_asset(self, name, model, category, age_years, 
                  battery_health=100, can_refurbish=True, is_hazardous=False):
        """Add a new asset to the inventory"""
        asset_id = f"ASSET-{self.next_id:04d}"
        self.next_id += 1
        
        asset = CampusAsset(
            asset_id, name, model, category, age_years,
            battery_health, can_refurbish, is_hazardous
        )
        
        self.assets[asset_id] = asset
        
        # Auto-process based on disposal strategy
        self._process_asset(asset)
        
        print(f"✓ SUCCESS: {asset.name} ({asset_id}) added to Circularity Engine.")
        print(f"  → Disposal Strategy: {asset.disposal_strategy.value}")
        return asset_id

    def _process_asset(self, asset):
        """Process asset based on its disposal strategy"""
        if asset.disposal_strategy == DisposalStrategy.MARKETPLACE:
            self.marketplace_items.append(asset.asset_id)
            print(f"  → Added to marketplace for sale/exchange")
        elif asset.disposal_strategy == DisposalStrategy.STRIP_COMPONENTS:
            print(f"  → Scheduled for component extraction")
        elif asset.disposal_strategy == DisposalStrategy.HAZARDOUS_DISPOSAL:
            print(f"  ⚠ HAZARDOUS: Special disposal protocol required")

    def delete_asset(self, asset_id):
        """Remove an asset from inventory"""
        if asset_id in self.assets:
            asset = self.assets[asset_id]
            del self.assets[asset_id]
            
            # Remove from marketplace if listed
            if asset_id in self.marketplace_items:
                self.marketplace_items.remove(asset_id)
            
            print(f"✓ DELETED: {asset.name} ({asset_id}) removed from inventory.")
            return True
        else:
            print(f"✗ ERROR: Asset {asset_id} not found.")
            return False

    def update_asset(self, asset_id, **kwargs):
        """Update asset properties"""
        if asset_id not in self.assets:
            print(f"✗ ERROR: Asset {asset_id} not found.")
            return False
        
        asset = self.assets[asset_id]
        
        # Update allowed fields
        for key, value in kwargs.items():
            if hasattr(asset, key):
                setattr(asset, key, value)
        
        # Re-evaluate disposal strategy after updates
        asset.disposal_strategy = asset.evaluate_disposal_strategy()
        
        print(f"✓ UPDATED: {asset.name} ({asset_id})")
        print(f"  → New Strategy: {asset.disposal_strategy.value}")
        return True

    def get_asset(self, asset_id):
        """Retrieve a specific asset"""
        return self.assets.get(asset_id)

    def list_all_assets(self):
        """Display all assets in inventory"""
        print("\n" + "="*80)
        print("FULL CAMPUS ASSET REPOSITORY")
        print("="*80)
        
        if not self.assets:
            print("No devices found. Add assets to begin tracking.")
            return
        
        for asset in self.assets.values():
            print(asset)
        
        print(f"\nTotal Assets: {len(self.assets)}")

    def search_assets(self, **criteria):
        """Search assets by various criteria"""
        results = []
        
        for asset in self.assets.values():
            match = True
            for key, value in criteria.items():
                if hasattr(asset, key):
                    if getattr(asset, key) != value:
                        match = False
                        break
            if match:
                results.append(asset)
        
        return results

    def check_procurement_prevention(self, device_name, device_category):
        """AI logic to prevent unnecessary purchases"""
        # Find dormant devices of same type
        dormant_matches = [
            asset for asset in self.assets.values()
            if asset.name.lower() == device_name.lower() 
            and asset.status == "Dormant"
            and asset.category == device_category
        ]
        
        if dormant_matches:
            print(f"\n⚠ [AI ALERT] PROCUREMENT BLOCKED!")
            print(f"  Found {len(dormant_matches)} dormant '{device_name}' in storage:")
            for asset in dormant_matches:
                print(f"  - {asset.asset_id}: Battery {asset.battery_health}%, "
                      f"Age {asset.age_years}yr")
            print(f"  → Recommendation: Use existing stock to prevent e-waste")
            return dormant_matches
        else:
            print(f"\n✓ [AI LOGIC] No dormant {device_name} found.")
            print(f"  New purchase approved for {device_category}")
            return None

    def show_marketplace(self):
        """Display items available for sale/exchange"""
        print("\n" + "="*80)
        print("CAMPUS MARKETPLACE - Refurbished Devices")
        print("="*80)
        
        if not self.marketplace_items:
            print("No items currently listed.")
            return
        
        for item_id in self.marketplace_items:
            asset = self.assets[item_id]
            print(f"📱 {asset.name} ({asset.model})")
            print(f"   Battery: {asset.battery_health}% | Age: {asset.age_years}yr | "
                  f"Price: Calculate based on condition")
            print()

    def generate_migration_report(self):
        """Generate report for transition to permanent campus"""
        print("\n" + "="*80)
        print("MIGRATION READINESS REPORT - Transit to Permanent Campus")
        print("="*80)
        
        strategies = {}
        for asset in self.assets.values():
            strategy = asset.disposal_strategy.value
            if strategy not in strategies:
                strategies[strategy] = []
            strategies[strategy].append(asset)
        
        for strategy, assets in strategies.items():
            print(f"\n{strategy}: {len(assets)} items")
            for asset in assets:
                print(f"  - {asset.asset_id}: {asset.name} ({asset.model})")

    def export_to_json(self, filename="inventory.json"):
        """Export inventory to JSON file"""
        data = {
            'assets': {aid: asset.to_dict() for aid, asset in self.assets.items()},
            'marketplace': self.marketplace_items,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ Inventory exported to {filename}")


def main_menu():
    """Interactive menu for the e-waste management system"""
    inventory = CampusInventory()
    
    # Pre-populate with some sample data
    print("Initializing IIT Delhi - Abu Dhabi Near-Zero E-Waste System...\n")
    
    while True:
        print("\n" + "="*80)
        print("NEAR-ZERO E-WASTE CAMPUS MANAGEMENT SYSTEM")
        print("="*80)
        print("1.  Add New Asset")
        print("2.  View All Assets")
        print("3.  Search Assets")
        print("4.  Update Asset")
        print("5.  Delete Asset")
        print("6.  Check Procurement (AI Prevention)")
        print("7.  View Marketplace")
        print("8.  Generate Migration Report")
        print("9.  Export Inventory to JSON")
        print("10. Exit")
        print("="*80)
        
        choice = input("\nEnter your choice (1-10): ").strip()
        
        if choice == "1":
            # Add asset
            print("\n--- Add New Asset ---")
            name = input("Device Name: ")
            model = input("Model: ")
            print("Categories: Laptop, Lab Equipment, Consumable, Appliance, Peripheral")
            category = input("Category: ")
            age_years = float(input("Age (years): "))
            battery_health = int(input("Battery Health % (0-100): "))
            can_refurbish = input("Can Refurbish? (y/n): ").lower() == 'y'
            is_hazardous = input("Contains Hazardous Materials? (y/n): ").lower() == 'y'
            
            inventory.add_asset(name, model, category, age_years, 
                              battery_health, can_refurbish, is_hazardous)
        
        elif choice == "2":
            inventory.list_all_assets()
        
        elif choice == "3":
            print("\n--- Search Assets ---")
            search_name = input("Search by name (or press Enter to skip): ")
            search_status = input("Search by status (or press Enter to skip): ")
            
            criteria = {}
            if search_name:
                criteria['name'] = search_name
            if search_status:
                criteria['status'] = search_status
            
            results = inventory.search_assets(**criteria)
            print(f"\nFound {len(results)} matching assets:")
            for asset in results:
                print(asset)
        
        elif choice == "4":
            asset_id = input("\nEnter Asset ID to update: ")
            asset = inventory.get_asset(asset_id)
            
            if asset:
                print(f"Current: {asset}")
                battery_health = input("New Battery Health (or Enter to skip): ")
                status = input("New Status (or Enter to skip): ")
                
                updates = {}
                if battery_health:
                    updates['battery_health'] = int(battery_health)
                if status:
                    updates['status'] = status
                
                inventory.update_asset(asset_id, **updates)
            else:
                print(f"Asset {asset_id} not found.")
        
        elif choice == "5":
            asset_id = input("\nEnter Asset ID to delete: ")
            inventory.delete_asset(asset_id)
        
        elif choice == "6":
            print("\n--- AI Procurement Prevention Check ---")
            device_name = input("Device Name to purchase: ")
            device_category = input("Device Category: ")
            inventory.check_procurement_prevention(device_name, device_category)
        
        elif choice == "7":
            inventory.show_marketplace()
        
        elif choice == "8":
            inventory.generate_migration_report()
        
        elif choice == "9":
            filename = input("Enter filename (default: inventory.json): ") or "inventory.json"
            inventory.export_to_json(filename)
        
        elif choice == "10":
            print("\nExiting system. Thank you!")
            break
        
        else:
            print("Invalid choice. Please try again.")


# Demo execution
if __name__ == "__main__":
    print("="*80)
    print("IIT DELHI - ABU DHABI: NEAR-ZERO E-WASTE SYSTEM")
    print("AI-Driven Prevention, Repurposing, and Circular Flows")
    print("="*80)
    
    # Quick demo
    demo = input("\nRun interactive demo? (y/n): ").lower()
    
    if demo == 'y':
        inventory = CampusInventory()
        
        # Add sample assets
        print("\n--- Adding Sample Assets ---")
        inventory.add_asset("Laptop", "ThinkPad X1", "Laptop", 1.5, 85, True, False)
        inventory.add_asset("Lab Refrigerator", "Samsung-400L", "Lab Equipment", 4.0, 100, False, False)
        inventory.add_asset("LED Bulb", "Philips-12W", "Consumable", 0.5, 100, False, True)
        inventory.add_asset("MacBook Pro", "M1-2021", "Laptop", 2.0, 90, True, False)
        
        inventory.list_all_assets()
        
        print("\n--- Testing AI Procurement Prevention ---")
        inventory.check_procurement_prevention("Laptop", "Laptop")
        
        inventory.show_marketplace()
        inventory.generate_migration_report()
        
        print("\n--- Starting Interactive Menu ---")
        main_menu()
    else:
        main_menu()