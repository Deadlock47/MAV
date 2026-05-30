import axios from "axios";

export const fetchManhwas = async () => {
    try {
        const response = await axios.get("http://127.0.0.1:8765/api/manhwa");
        console.log("Fetched manhwas:", response.data);
        return response.data?.items ?? [];
    } catch (error) {
        console.error("Error fetching manhwas:", error);
        return [];
    }
};

export const fetchManhwaSlug = async (slug)=>{
    try {
        const response = await axios.get(`http://127.0.0.1:8765/api/manhwa/${slug}`)
        console.log("Fetched For", slug , response.data);
        return response.data ?? {}
 
    } catch (error) {
        console.error("Error fetching manhwas:", error);
        return {};
    }
}

export const scrapeManhwa = async (url) => {
    try {
        const response = await axios.get(`http://127.0.0.1:8765/api/manhwa/fetch/?url=${url}`);
        console.log("Scraped manhwa:", response.data);
        return response.data;
    } catch (error) {
        console.error("Error scraping manhwa:", error);
        return null;
    }
};

export const scrapeChapter = async (slug,chapter_number) => {
    try {
        const response = await axios.get(`http://127.0.0.1:8765/api/manhwa/${slug}/chapters/${chapter_number}`);
        console.log("Scraped manhwa:", response.data);
        return response.data;
    } catch (error) {
        console.error("Error scraping manhwa:", error);
        return null;
    }
};