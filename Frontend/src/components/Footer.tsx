import { MapPin, Phone, Mail, Facebook, Instagram, Twitter } from "lucide-react";
import { Button } from "@/components/ui/button";
import mahalaxmiLogo from "@/assets/mahalaxmi-logo.png";

const Footer = () => {
  return (
    <footer className="bg-gradient-to-br from-[hsl(213,89%,42%)] to-[hsl(271,81%,56%)] text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Company Info */}
          <div className="space-y-4">
            <img 
              src={mahalaxmiLogo} 
              alt="Mahalaxmi Tours And Travel" 
              className="h-12 w-auto brightness-0 invert"
            />
            <p className="text-white/90 text-sm leading-relaxed">
              Your trusted partner for unforgettable Nepal adventures. Experience the beauty of the Himalayas with our expert guides and carefully crafted tour packages.
            </p>
            <div className="flex space-x-3">
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0 hover:bg-white/10 text-white">
                <Facebook className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0 hover:bg-white/10 text-white">
                <Instagram className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0 hover:bg-white/10 text-white">
                <Twitter className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Quick Links */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">Quick Links</h3>
            <ul className="space-y-2 text-sm">
              <li><a href="#home" className="text-white/80 hover:text-[hsl(45,93%,47%)] transition-colors">Home</a></li>
              <li><a href="#packages" className="text-white/80 hover:text-[hsl(45,93%,47%)] transition-colors">Tour Packages</a></li>
              <li><a href="#about" className="text-white/80 hover:text-[hsl(45,93%,47%)] transition-colors">About Us</a></li>
              <li><a href="#contact" className="text-white/80 hover:text-[hsl(45,93%,47%)] transition-colors">Contact</a></li>
              <li><a href="#" className="text-white/80 hover:text-[hsl(45,93%,47%)] transition-colors">Blog</a></li>
              <li><a href="#" className="text-white/80 hover:text-[hsl(45,93%,47%)] transition-colors">Gallery</a></li>
            </ul>
          </div>

          {/* Popular Destinations */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">Popular Destinations</h3>
            <ul className="space-y-2 text-sm">
              <li><a href="#" className="text-white/80 hover:text-[hsl(45,93%,47%)] transition-colors">Everest Base Camp</a></li>
              <li><a href="#" className="text-white/80 hover:text-[hsl(45,93%,47%)] transition-colors">Annapurna Circuit</a></li>
              <li><a href="#" className="text-white/80 hover:text-[hsl(45,93%,47%)] transition-colors">Kathmandu Valley</a></li>
              <li><a href="#" className="text-white/80 hover:text-[hsl(45,93%,47%)] transition-colors">Chitwan National Park</a></li>
              <li><a href="#" className="text-white/80 hover:text-[hsl(45,93%,47%)] transition-colors">Pokhara</a></li>
              <li><a href="#" className="text-white/80 hover:text-[hsl(45,93%,47%)] transition-colors">Langtang Valley</a></li>
            </ul>
          </div>

          {/* Contact Info */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">Contact Us</h3>
            <div className="space-y-3 text-sm">
              <div className="flex items-start space-x-3">
                <MapPin className="h-5 w-5 mt-0.5 flex-shrink-0 text-[hsl(45,93%,47%)]" />
                <span className="text-white/90">Thamel, Kathmandu<br />Nepal 44600</span>
              </div>
              <div className="flex items-center space-x-3">
                <Phone className="h-5 w-5 flex-shrink-0 text-[hsl(45,93%,47%)]" />
                <span className="text-white/90">+977-1-4123456</span>
              </div>
              <div className="flex items-center space-x-3">
                <Mail className="h-5 w-5 flex-shrink-0 text-[hsl(45,93%,47%)]" />
                <span className="text-white/90">info@mahalaxmi.com</span>
              </div>
            </div>
            <div className="pt-4">
              <Button className="bg-gradient-to-r from-[hsl(25,95%,53%)] to-[hsl(45,93%,47%)] text-white border-0 hover:from-[hsl(25,95%,48%)] hover:to-[hsl(45,93%,42%)]" size="sm">
                Get Quote
              </Button>
            </div>
          </div>
        </div>

        <div className="border-t border-white/20 mt-8 pt-8 text-center text-sm text-white/80">
          <p>&copy; 2024 Mahalaxmi Tours And Travel. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;