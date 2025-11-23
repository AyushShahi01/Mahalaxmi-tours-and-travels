import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Card, CardContent } from "@/components/ui/card";
import { MapPin, Users, Award, Globe } from "lucide-react";

const About = () => {
  const stats = [
    { icon: Users, label: "Happy Travelers", value: "10,000+" },
    { icon: Award, label: "Years Experience", value: "15+" },
    { icon: MapPin, label: "Tour Destinations", value: "50+" },
    { icon: Globe, label: "Countries Served", value: "25+" },
  ];

  const team = [
    {
      name: "Ram Bahadur Shrestha",
      role: "Founder & CEO",
      experience: "20+ years in tourism industry",
      speciality: "Himalayan expeditions"
    },
    {
      name: "Sita Kumari Gurung",
      role: "Operations Manager", 
      experience: "15+ years in tour operations",
      speciality: "Cultural heritage tours"
    },
    {
      name: "Birendra Tamang",
      role: "Senior Trek Guide",
      experience: "18+ years trekking guide",
      speciality: "High altitude trekking"
    }
  ];

  return (
    <div className="min-h-screen">
      <Navbar />
      
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-primary via-primary/80 to-secondary pt-20 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center text-white">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">About Mahalaxmi Tours</h1>
            <p className="text-xl md:text-2xl max-w-3xl mx-auto opacity-90">
              Your trusted partner for authentic Nepal experiences since 2009
            </p>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => {
              const IconComponent = stat.icon;
              return (
                <div key={index} className="text-center">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-primary/10 rounded-full mb-4">
                    <IconComponent className="h-8 w-8 text-primary" />
                  </div>
                  <div className="text-3xl font-bold text-foreground mb-2">{stat.value}</div>
                  <div className="text-muted-foreground">{stat.label}</div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Our Story */}
      <section className="py-16 bg-muted/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">Our Story</h2>
            <div className="prose prose-lg max-w-none text-muted-foreground">
              <p className="text-lg leading-relaxed mb-6">
                Founded in 2009 by passionate locals who believe Nepal's natural beauty and cultural richness 
                should be shared with the world, Mahalaxmi Tours and Travel has grown from a small family business 
                into one of Nepal's most trusted tour operators.
              </p>
              <p className="text-lg leading-relaxed mb-6">
                Our journey began with a simple mission: to provide authentic, sustainable, and memorable travel 
                experiences that benefit both visitors and local communities. Over the years, we've refined our 
                approach, always staying true to our core values of safety, authenticity, and respect for nature.
              </p>
              <p className="text-lg leading-relaxed">
                Today, we're proud to have facilitated life-changing adventures for thousands of travelers from 
                around the globe, while maintaining our commitment to responsible tourism and community development.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-16 bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">Meet Our Team</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 md:gap-8">
            {team.map((member, index) => (
              <Card key={index} className="text-center">
                <CardContent className="pt-6">
                  <div className="w-24 h-24 bg-primary/10 rounded-full mx-auto mb-4 flex items-center justify-center">
                    <Users className="h-12 w-12 text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{member.name}</h3>
                  <p className="text-primary font-medium mb-2">{member.role}</p>
                  <p className="text-sm text-muted-foreground mb-2">{member.experience}</p>
                  <p className="text-sm font-medium">Speciality: {member.speciality}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Mission & Values */}
      <section className="py-16 bg-muted/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            <div>
              <h2 className="text-3xl font-bold mb-6">Our Mission</h2>
              <p className="text-muted-foreground text-lg leading-relaxed">
                To create exceptional travel experiences that showcase Nepal's natural wonders and cultural heritage 
                while promoting sustainable tourism practices that benefit local communities and preserve our 
                environment for future generations.
              </p>
            </div>
            <div>
              <h2 className="text-3xl font-bold mb-6">Our Values</h2>
              <ul className="space-y-4 text-muted-foreground">
                <li className="flex items-start">
                  <Award className="h-5 w-5 text-primary mt-1 mr-3 flex-shrink-0" />
                  <span><strong>Safety First:</strong> Your wellbeing is our top priority</span>
                </li>
                <li className="flex items-start">
                  <Globe className="h-5 w-5 text-primary mt-1 mr-3 flex-shrink-0" />
                  <span><strong>Authentic Experiences:</strong> Real connections with local culture</span>
                </li>
                <li className="flex items-start">
                  <Users className="h-5 w-5 text-primary mt-1 mr-3 flex-shrink-0" />
                  <span><strong>Community Support:</strong> Tourism that benefits locals</span>
                </li>
                <li className="flex items-start">
                  <MapPin className="h-5 w-5 text-primary mt-1 mr-3 flex-shrink-0" />
                  <span><strong>Environmental Responsibility:</strong> Protecting Nepal's natural beauty</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default About;