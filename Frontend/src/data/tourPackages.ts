import { getTours } from "@/api/toures_api";

export interface TourPackage {
  id: number;
  title: string;
  description: string;
  duration: string;
  groupSize: string;
  price: number;
  image: string;
  highlights: string[];
  itinerary: string[];
  included: string[];
  excluded: string[];
}

// API Response interface to handle field mismatches
interface ApiTourPackage {
  id: number;
  name?: string;           // API uses 'name' instead of 'title'
  title?: string;
  description?: string;
  duration?: string;
  group_size?: string;     // API uses 'group_size' instead of 'groupSize'
  groupSize?: string;
  price: number;
  cover_image?: string;    // API uses 'cover_image' for image
  image_url?: string;      // Alternative name
  highlights?: string | string[];
  tour_highlights?: string | string[];  // Alternative name for highlights
  tours?: string | string[];            // API might use 'tours' for highlights
  itinerary?: string | string[];
  tour_details?: string | string[];     // API uses 'tour_details' for itinerary
  details?: string | string[];          // Another alternative
  included?: string | string[];
  excluded?: string | string[];
  [key: string]: any;  // Allow other fields
}

// Helper function to parse string to array (handles comma-separated or line-break separated)
const parseToArray = (value: string | string[] | undefined): string[] => {
  if (!value) return [];
  if (Array.isArray(value)) return value;
  
  // Try to parse as JSON first
  try {
    const parsed = JSON.parse(value);
    if (Array.isArray(parsed)) return parsed;
  } catch {
    // If not JSON, split by common delimiters
    if (value.includes('\n')) {
      return value.split('\n').map(item => item.trim()).filter(item => item.length > 0);
    }
    if (value.includes(',')) {
      return value.split(',').map(item => item.trim()).filter(item => item.length > 0);
    }
  }
  
  return [value];
};

// Transform API data to match our TourPackage interface
const transformApiData = (apiData: ApiTourPackage): TourPackage => {
  // Handle highlights - check multiple possible field names
  const highlightsData = apiData.tours || apiData.tour_highlights || apiData.highlights;
  
  // Handle itinerary - the API uses 'tour_details' for itinerary
  const itineraryData = apiData.tour_details || apiData.details || apiData.itinerary;
  
  return {
    id: apiData.id,
    title: apiData.name || apiData.title || 'Untitled Tour',
    description: apiData.description || '',
    duration: apiData.duration || 'N/A',
    groupSize: apiData.group_size || apiData.groupSize || 'N/A',
    price: apiData.price || 0,
    image: apiData.cover_image || apiData.image_url || '',  // Map cover_image from API to image field
    highlights: parseToArray(highlightsData),
    itinerary: parseToArray(itineraryData),
    included: parseToArray(apiData.included),
    excluded: parseToArray(apiData.excluded),
  };
};

// Cache for tour packages
let cachedTourPackages: TourPackage[] | null = null;

// Fetch and transform tour packages from API
export const fetchTourPackages = async (): Promise<TourPackage[]> => {
  try {
    console.log("Fetching tour packages from API...");
    const apiData = await getTours();
    console.log("API Response:", apiData);
    
    if (Array.isArray(apiData) && apiData.length > 0) {
      // Log the first item to see field names
      console.log("First API item fields:", Object.keys(apiData[0]));
      console.log("First API item:", apiData[0]);
      
      cachedTourPackages = apiData.map(transformApiData);
      console.log("Transformed packages:", cachedTourPackages);
      console.log("First transformed package:", cachedTourPackages[0]);
      return cachedTourPackages;
    }
    
    console.warn("No tour data returned from API, using empty array");
    return [];
  } catch (error) {
    console.error("Error fetching tour packages:", error);
    return [];
  }
};

// Get tour packages (returns cached data if available)
export const getTourPackages = async (): Promise<TourPackage[]> => {
  if (cachedTourPackages) {
    return cachedTourPackages;
  }
  return await fetchTourPackages();
};

// Get tour by ID
export const getTourById = async (id: number): Promise<TourPackage | undefined> => {
  const packages = await getTourPackages();
  return packages.find(tour => tour.id === id);
};

// Synchronous version for backwards compatibility (returns cached data or empty array)
export const tourPackages: TourPackage[] = [];
