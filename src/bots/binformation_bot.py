from src.core.bot_base import BotBase
from src.utils.database import db
from datetime import date, timedelta

class BinformationBot(BotBase):
    
    def prepare_message(self):
        tomorrow = date.today() + timedelta(days=1)
        
        collections = db.get_bin_collections(
            start_date=tomorrow,
            end_date=tomorrow,
            is_completed=False
        )
        
        if not collections:
            return None  # No collections tomorrow, don't send message
        
        # Format the message
        bin_types = [col[2] for col in collections]  # col[2] is bin_type
        bins_text = ', '.join(bin_types)
        
        message = f"🗑️ Bin Reminder!\n\n"
        message += f"Put out the following bins tonight:\n"
        for bin_type in bin_types:
            message += f"  • {bin_type}\n"
        message += f"\nCollection day: {tomorrow.strftime('%A, %d %B %Y')}"
        
        return message
