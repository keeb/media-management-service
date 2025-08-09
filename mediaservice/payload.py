"""
Handles conversion of a payload and provides helper methods
{
    "images": [
      "https://d1a0n9gptf7ayu.cloudfront.net/photos/66383444b6f39fc42dc13c6461edac39.jpg",
      "https://d1a0n9gptf7ayu.cloudfront.net/photos/28cb406560ce294a6ef55e1b07969957.jpg",
      "https://d1a0n9gptf7ayu.cloudfront.net/photos/db791999fe79e650a36b2a19f0798745.jpg",
      "https://d1a0n9gptf7ayu.cloudfront.net/photos/08d29c4064a2139192ba3aff0116ae1a.jpg",
      "https://d1a0n9gptf7ayu.cloudfront.net/photos/8c4427dbbe1139a8f068de713127b9e5.jpg",
      "https://d1a0n9gptf7ayu.cloudfront.net/photos/4628f3407d016ea5a2bfad1a469ee998.jpg",
      "https://d1a0n9gptf7ayu.cloudfront.net/photos/c156a7e138f0d989f0447ca868e736c8.jpg",
      "https://d1a0n9gptf7ayu.cloudfront.net/photos/39762b033f18087872e090dbb8ffecf1.jpg",
      "https://d1a0n9gptf7ayu.cloudfront.net/photos/0ae4c8dc99bcf06b2052680ef651364d.jpg",
      "https://d1a0n9gptf7ayu.cloudfront.net/photos/48806504a15e57d65ed7b5422390619e.jpg",
      "https://d1a0n9gptf7ayu.cloudfront.net/photos/1d2e52f6ada432545caf4e17faca6095.jpg",
      "https://d1a0n9gptf7ayu.cloudfront.net/photos/efa060018c273bba4a3009c39546ed5d.jpg",
      "https://d1a0n9gptf7ayu.cloudfront.net/photos/ddceaf3261d146abb6a57ca28ca82d28.jpg",
      "https://d1a0n9gptf7ayu.cloudfront.net/photos/47d9e698d7fbf504c86875c54c07361e.jpg",
      "https://d1a0n9gptf7ayu.cloudfront.net/photos/b8fc11cd0ae3c7a37af8a86872dfc328.jpg",
      "https://d1a0n9gptf7ayu.cloudfront.net/photos/d5423e9882ccbdd0cda881355b46a0d8.jpg",
      "https://d1a0n9gptf7ayu.cloudfront.net/photos/03053ae03cb15b20feb3ff02f6280a91.jpg"
    ],
    "album": "Coffee and Whiskers",
    "model": "Lust",
    "socials": [
      "https://instagram.com/lustsuicide",
      "https://twitter.com/LustSuicide",
      "https://onlyfans.com/lust_",
      "https://allmylinks.com/lust"
    ]
}
"""

class Payload:
    def __init__(self, payload):
        self._payload_dict = payload
        self.unique_id = None
        self.model = None
        self.album = None
        self.socials = None
        self.images = None
        try:
            self._parse(payload)
        except:
            raise Exception("ur payload sux")
    
    def _parse(self, payload):
        try:
            self.unique_id = payload.get("_id")
        except:
            # not from mongodb
            pass

        model_name = payload.get("model")
        album_name = payload.get("album")
        image_list = payload.get("images")
        socials_list = payload.get("socials")

        self.model = self._sanitize(model_name)
        self.album = self._sanitize(album_name)
        self.images = image_list
        self.socials = socials_list

    def dict(self):
        if self.mongo():
            del self._payload_dict["_id"]
        return self._payload_dict    
    
    def _sanitize(self, name):
        name = name.replace(" ", "-")
        name = name.replace("(", "")
        name = name.replace(")", "")
        name = name.replace(",", "")
        name = name.replace("?", "")
        name = name.replace("&", "and")
        name = name.lower()
        return name

    def __repr__(self):
        return "%s - %s [%s][%s]" % (self.model, self.album, len(self.socials), len(self.images))    
        
    def mongo(self):
        """ 
            was this initialized from mongo or can it be found in mongo
        """
        if self.unique_id == None or self._payload_dict.get("_id") == None: 
            return False
        return True
    