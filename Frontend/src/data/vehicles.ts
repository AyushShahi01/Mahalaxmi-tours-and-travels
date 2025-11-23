export interface Vehicle {
  id: number;
  name: string;
  type: string;
  capacity: number;
  description: string;
  features: string[];
  image: string;
  pricePerDay: number;
}

export const vehicles: Vehicle[] = [
  {
    id: 1,
    name: "4x4 SUV",
    type: "Off-Road Vehicle",
    capacity: 5,
    description: "Perfect for mountain terrain and rugged roads. Comfortable and reliable for long journeys.",
    features: ["Air Conditioning", "GPS Navigation", "Music System", "Power Steering"],
    image: "/src/assets/suv-vehicle.jpg",
    pricePerDay: 120
  },
  {
    id: 2,
    name: "Tourist Bus",
    type: "Large Bus",
    capacity: 35,
    description: "Spacious tourist bus ideal for group tours with comfortable seating and modern amenities.",
    features: ["Air Conditioning", "Reclining Seats", "Entertainment System", "Luggage Space"],
    image: "/src/assets/tourist-bus.jpg",
    pricePerDay: 250
  },
  {
    id: 3,
    name: "Luxury Van",
    type: "Mini Van",
    capacity: 12,
    description: "Perfect for small groups seeking comfort and style during their Nepal adventure.",
    features: ["Air Conditioning", "Leather Seats", "WiFi", "Refreshments"],
    image: "/src/assets/luxury-van.jpg",
    pricePerDay: 180
  },
  {
    id: 4,
    name: "Jeep Safari",
    type: "Safari Jeep",
    capacity: 7,
    description: "Rugged jeep perfect for jungle safari and off-road mountain adventures.",
    features: ["4x4 Drive", "Open Top Option", "Safari Gear", "Experienced Driver"],
    image: "/src/assets/safari-jeep.jpg",
    pricePerDay: 150
  },
  {
    id: 5,
    name: "Standard Sedan",
    type: "Car",
    capacity: 4,
    description: "Comfortable sedan for city tours and airport transfers with professional drivers.",
    features: ["Air Conditioning", "GPS", "Music System", "Child Seat Available"],
    image: "/src/assets/sedan-car.jpg",
    pricePerDay: 80
  },
  {
    id: 6,
    name: "Mini Bus",
    type: "Medium Bus",
    capacity: 20,
    description: "Ideal for medium-sized groups, offering comfort and reliability for tour excursions.",
    features: ["Air Conditioning", "Comfortable Seats", "Audio System", "Large Windows"],
    image: "/src/assets/mini-bus.jpg",
    pricePerDay: 200
  }
];
