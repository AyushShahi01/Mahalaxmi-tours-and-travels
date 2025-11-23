import axios from 'axios';
import { BASE_URL } from './base_api';

const base_api = BASE_URL;

export const getTours = async () => {
    try {
        const response = await axios.get(`${base_api}/api/toures/packages`);
        return response.data;
    } catch (error) {
        console.error("Error fetching tours:", error);
        return [];
    }   
};