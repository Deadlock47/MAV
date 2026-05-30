import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom';
import {useSearchParams} from 'react-router-dom';
import { scrapeChapter } from '../Helpers/Fetchs';
import { useNavigate } from "react-router-dom";

function ChapterDetail() {
      const [searchParams] = useSearchParams();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [chapter,setChapter] = useState();
    const [imageWidth, setImageWidth] = useState(60);
//   const url = searchParams.get("url");
    const navigate = useNavigate();

    const {slug} = useParams();
    const {chapter_number} = useParams();
    console.log(typeof chapter_number)
    async function getData(slug,chapter_number) {
    setLoading(true);
    setError(null);
    try {
        const items = await scrapeChapter(slug,chapter_number);
        setChapter(items);
    } catch (err) {
        console.error("Failed to load manhwas:", err);
        setError("Unable to load manhwas. Please try again.");
    } finally {
        setLoading(false);
    }
    }
    useEffect(() => {
        getData(slug,chapter_number);
    }, [slug,chapter_number]);
  return (
    <div>
             <div className='fixed bottom-0 right-10'>

                <label className='flex items-center gap-3 bg-white text-neutral-800 w-fit px-4 py-2 rounded-t-2xl text-sm'>
                    -
                    <input
                        type="range"
                        min="30"
                        max="100"
                        value={imageWidth}
                        onChange={(event) => setImageWidth(event.target.value)}
                        className='w-48 accent-purple-600'
                    />
                    +
                    {/* <span className='w-12 text-right'>{imageWidth}%</span> */}
                </label>
            </div>
             <div className='fixed bottom-0 flex flex-row gap-1 left-10'>

               <div 
                  onClick={() => navigate(`/manhwa/${slug}/chapter/${Number(chapter_number) > 1 ? Number(chapter_number)-1 : Number(chapter_number)}`)}
          
               className="p-4 py-2 text-white rounded-t-xl  bg-neutral-400/70 cursor-pointer backdrop-blur-lg  border border-neutral-800 shadow-2xl"> {"<"} Prev</div>
               <div 
                  onClick={() => navigate(`/manhwa/${slug}/chapter/${Number(chapter_number) > 0 ? Number(chapter_number)+1 : Number(chapter_number)}`)}

               className="p-4 py-2 text-white rounded-t-xl  bg-neutral-400/70 cursor-pointer backdrop-blur-lg  border border-neutral-800 shadow-2xl">Next {">"}</div>
            </div>
        <div className='text-white text-3xl font-bold w-full underline glassmorphism dark:glassmorphism-dark flex flex-col gap-3 items-center p-2 md:p-2' >
            {chapter?.chapter_title}
        </div>
        
        <div className='flex flex-wrap items-center gap-4 ml-32 mt-4'>
            <div className='text-md bg-white text-neutral-800 w-fit p-4 py-1 rounded-2xl text-xl'>
                Pages : {chapter?.number_of_pages}
            </div>
       

        </div>
        <div className='flex flex-col items-center mt-4'>
            {
                chapter?.pages.map((page,index) => (
                    <img loading="lazy" style={{ width: `${imageWidth}%` }}  src={page} alt={page} key={index} />
                ))
            }
        </div>
    </div>
  )
}

export default ChapterDetail
