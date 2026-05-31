import axios from "axios";

export const fetchJavs = async (limit,offset,release_date) => {
    try {
        const response = await axios.get("http://127.0.0.1:8765/api/jav/videos?limit="+limit+"&offset="+offset+"&release_date="+release_date);
        console.log("Fetched manhwas:", response.data);
        return response.data ?? {};
    } catch (error) {
        console.error("Error fetching JAVS:", error);
        return [];
    }
};

export const fetchJavDetails = async (dvd_id) => {
     try {
        const response = await axios.get("http://127.0.0.1:8765/api/videos/details?dvd_id="+dvd_id);
        console.log("Fetched manhwas:", response.data);
        return response.data ?? {};
    } catch (error) {
        console.error("Error fetching JAV details:",dvd_id, error);
        return [];
    }
}

export const fetchTrailer = async (dvd_id) => {
    try {
        const response = await axios.get("http://127.0.0.1:8765/api/video/trailer?dvd_id="+dvd_id);
        console.log("Fetched Trailers:", response.data);
        return response.data ?? {};
    } catch (error) {
        console.error("Error fetching JAV details:",dvd_id, error);
        return [];
    }
}

export const fetchFullVideo = async (dvd_id)=>{
    try {
        const response = await axios.get("http://127.0.0.1:8765/api/video/fullVideo?dvd_id="+dvd_id);
        console.log("Fetched Videos:",response.data);
        return response.data ?? {};
    } catch (error) {
         console.error("Error fetching JAV Full Video details:",dvd_id, error);
        return [];
    }
}
