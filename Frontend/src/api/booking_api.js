import axios from 'axios';
import { BASE_URL } from './base_api';

const base_api = BASE_URL;

// Initiate eSewa v2 payment - returns payment form data with HMAC signature
export const bookWithEsewa = async (bookingData) => {
    try {
        // Validate required fields before sending
        const requiredFields = ['package_id', 'payment_amount', 'traveler_name', 'traveler_email', 'traveler_phone', 'traveler_address'];
        const missingFields = requiredFields.filter(field => !bookingData[field]);
        
        if (missingFields.length > 0) {
            throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
        }

        console.log('Booking data being sent:', bookingData);
        
        const response = await axios.post(`${base_api}/api/system/book-with-esewa/`, bookingData);
        
        console.log('Backend response:', response.data);
        
        // Validate response structure
        if (!response.data.success) {
            throw new Error(response.data.message || 'Payment initiation failed');
        }
        
        if (!response.data.payment_url || !response.data.payment_form_data) {
            throw new Error('Invalid payment response from server');
        }
        
        return response.data;
    } catch (error) {
        console.error("Error initiating eSewa payment:", error);
        
        // Provide detailed error information
        if (error.response?.data) {
            console.error("Server error details:", error.response.data);
            // Throw the server error with detailed information
            throw new Error(error.response.data.error || error.response.data.message || 'Server error');
        }
        
        throw error;
    }   
};
