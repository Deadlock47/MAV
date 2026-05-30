import React, { useEffect, useState } from 'react'
import { useParams } from "react-router-dom";
import { fetchManhwaSlug } from '../Helpers/Fetchs';
import {useNavigate} from 'react-router-dom';
function ManhwaDetail() {
    const navigate = useNavigate();
    const {slug} = useParams();
    const [manhwa , setManhwa] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

      async function getData(slug) {
        setLoading(true);
        setError(null);
        try {
          const items = await fetchManhwaSlug(slug);
          setManhwa(items);
        } catch (err) {
          console.error("Failed to load manhwas:", err);
          setError("Unable to load manhwas. Please try again.");
        } finally {
          setLoading(false);
        }
      }
    useEffect(() => {
        getData(slug);
        console.log(manhwa)
    },[])
  return (
    <div className='text-white w-full glassmorphism dark:glassmorphism-dark flex flex-col gap-3 items-center p-2 md:p-2' >
        
        <div className='text-4xl font-bold'>{manhwa.title}</div>
        <div className='flex -600 w-11/12 flex-row mx-32 gap-2'>
            <div className=" h-[100%] p-10 w-[450px]">
                <img className="w-full h-full rounded-2xl" src={manhwa.poster_url} alt={manhwa.poster_url} srcset="" />
            </div>
            {/* <div className=" w-[1px] h-full">
            <br></br>
            </div> */}
            <div className=" justify-items-start pt-20 flex flex-col  pl-[10px] w-3/4 " >
                <div className="text-[22px] ">• Author : {manhwa.authors}</div>
                <div className="text-[22px] ">• No of Chapters : {manhwa.number_of_chapters}</div>
                <div className="text-[22px] ">• Artist : {manhwa.artists}</div >
                <div className='text-[22px] '>• Rating : {manhwa.rating}</div>
                <div className='text-[22px] '>• Status : {manhwa.status}</div>
                {/* Tags */}
                <div className="flex flex-row text-[22px] pt-5 pl-2 flex-wrap gap-2">
                   Tags : {
                        manhwa.tags?.map((tag , index) => (
                            <div  key={index} className="bg-zinc-900/70 backdrop-blur-lg rounded-2xl border p-1 px-2 border-zinc-800 shadow-2xl text-[20px]">{tag}</div>
                        ))
                    }
                </div>
        
              
            </div>
        </div>
        <div className='flex flex-col w-11/12 gap-2'>
            <div className='text-2xl font-bold'>Description</div>
            <div className='text-[20px]'>{manhwa.description}</div>
        </div>
        {/* Chapters */}
        <div className="flex flex-col w-11/12 gap-2">
            <div className='text-2xl font-bold'>Chapters</div>
            <div className="flex flex-col text-[22px] pt-5 pl-2 flex-wrap gap-2" >
                {
                    manhwa?.all_chapters?.map((chapter , index) => (
                        <div
                        onClick={() => navigate(`/manhwa/${manhwa.slug}/chapter/${chapter.chapter_number}?url=${chapter.url}`)}
                        key={chapter.chapter_number} className="bg-zinc-900/70 backdrop-blur-lg rounded-2xl border p-1 px-2 border-zinc-800 shadow-2xl text-[20px]">{chapter.title}</div>
                    ))
                }
            </div>

        </div>
    </div>
  )
}

export default ManhwaDetail