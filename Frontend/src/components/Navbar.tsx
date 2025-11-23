import { useState, useEffect } from "react";
import { Menu, X, Phone, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import mahalaxmiLogo from "@/assets/mahalaxmi-logo-2.png";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const [lastScrollY, setLastScrollY] = useState(0);

  useEffect(() => {
    const controlNavbar = () => {
      if (typeof window !== 'undefined') { 
        if (window.scrollY > lastScrollY && window.scrollY > 100) {
          // Scrolling down
          setIsVisible(false);
        } else if (window.scrollY < lastScrollY) {
          // Scrolling up
          setIsVisible(true);
        }
        setLastScrollY(window.scrollY);
      }
    };

    if (typeof window !== 'undefined') {
      window.addEventListener('scroll', controlNavbar);
      return () => {
        window.removeEventListener('scroll', controlNavbar);
      };
    }
  }, [lastScrollY]);

  const navItems = [
    { name: "Home", href: "/" },
    { name: "Tour Packages", href: "/#packages" },
    { name: "Vehicles", href: "/vehicles" },
    { name: "About Us", href: "/about" },
    { name: "Contact", href: "/contact" },
  ];

  return (
    <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${
      isVisible 
        ? 'bg-background/20 backdrop-blur-sm border-b border-white/10 translate-y-0' 
        : 'bg-transparent border-transparent -translate-y-full'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <a href="/" className="flex items-center space-x-3 cursor-pointer">
            <img 
              src={mahalaxmiLogo} 
              alt="Mahalaxmi Tours And Travel" 
              className="h-12 w-auto object-contain"
            />
          </a>

          {/* Desktop Navigation */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-8">
              {navItems.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className="text-foreground hover:text-primary px-3 py-2 text-sm font-medium transition-colors"
                >
                  {item.name}
                </a>
              ))}
            </div>
          </div>

          {/* Contact Info */}
          <div className="hidden lg:flex items-center space-x-4">
            <div className="flex items-center text-sm ">
              <Phone className="h-4 w-4 mr-1" />
              +977-9865072766
            </div>
            <div className="flex items-center text-sm ">
              <Mail className="h-4 w-4 mr-1" />
              info@mahalaxmi.com
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsOpen(!isOpen)}
            >
              {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-background border-t">
              {navItems.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className="block px-3 py-2 text-base font-medium text-foreground hover:text-primary transition-colors"
                  onClick={() => setIsOpen(false)}
                >
                  {item.name}
                </a>
              ))}
              <div className="pt-2 border-t">
                <div className="px-3 py-2 text-sm text-muted-foreground">
                  <Phone className="h-4 w-4 inline mr-2" />
                  +977-1-4123456
                </div>
                <div className="px-3 py-2 text-sm text-muted-foreground">
                  <Mail className="h-4 w-4 inline mr-2" />
                  info@mahalaxmi.com
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;