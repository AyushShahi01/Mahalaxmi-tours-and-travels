import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import TourPackages from "@/components/TourPackages";
import Footer from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen">
      <Navbar />
      <Hero />
      <TourPackages />
      <Footer />
    </div>
  );
};

export default Index;
