import json
import os

class BotConfig:
    """Configuration manager for the Discord bot"""
    
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default config
            default_config = {
                "channel_whitelist": [],
                "admin_users": []
            }
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
    
    def get_channel_whitelist(self):
        """Get list of whitelisted channel IDs"""
        return self.config.get('channel_whitelist', [])
    
    def add_channel(self, channel_id):
        """Add a channel to the whitelist"""
        if not isinstance(channel_id, str):
            channel_id = str(channel_id)
            
        whitelist = self.get_channel_whitelist()
        if channel_id not in whitelist:
            whitelist.append(channel_id)
            self.config['channel_whitelist'] = whitelist
            self.save_config()
            return True
        return False
    
    def remove_channel(self, channel_id):
        """Remove a channel from the whitelist"""
        if not isinstance(channel_id, str):
            channel_id = str(channel_id)
            
        whitelist = self.get_channel_whitelist()
        if channel_id in whitelist:
            whitelist.remove(channel_id)
            self.config['channel_whitelist'] = whitelist
            self.save_config()
            return True
        return False
    
    def get_admin_users(self):
        """Get list of admin user IDs"""
        return self.config.get('admin_users', [])
    
    def add_admin(self, user_id):
        """Add a user to the admin list"""
        if not isinstance(user_id, str):
            user_id = str(user_id)
            
        admins = self.get_admin_users()
        if user_id not in admins:
            admins.append(user_id)
            self.config['admin_users'] = admins
            self.save_config()
            return True
        return False
    
    def remove_admin(self, user_id):
        """Remove a user from the admin list"""
        if not isinstance(user_id, str):
            user_id = str(user_id)
            
        admins = self.get_admin_users()
        if user_id in admins:
            admins.remove(user_id)
            self.config['admin_users'] = admins
            self.save_config()
            return True
        return False
    
    def is_admin(self, user_id):
        """Check if a user is an admin"""
        if not isinstance(user_id, str):
            user_id = str(user_id)
            
        return user_id in self.get_admin_users()
    
    def is_channel_whitelisted(self, channel_id):
        """Check if a channel is whitelisted"""
        if not isinstance(channel_id, str):
            channel_id = str(channel_id)
            
        whitelist = self.get_channel_whitelist()
        # If whitelist is empty, all channels are allowed
        return len(whitelist) == 0 or channel_id in whitelist
