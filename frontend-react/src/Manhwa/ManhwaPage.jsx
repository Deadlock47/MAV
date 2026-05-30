import { useEffect, useState } from "react";
import { fetchManhwas, scrapeManhwa } from "./Helpers/Fetchs";
import Mhw_Items from "../components/Mhw_Items";
import { NavLink } from "react-router-dom";


function ManhwaPage() {

  const [query, setQuery] = useState("");
  const [showAddInput, setShowAddInput] = useState(false);
  const [newUrl, setNewUrl] = useState("");
  const [manhwas, setManhwas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const handleSubmit = (event) => {
    event.preventDefault();
    onSearch?.(query.trim());
  };

  async function getData() {
    setLoading(true);
    setError(null);
    try {
      const items = await fetchManhwas();
      setManhwas(items);
    } catch (err) {
      console.error("Failed to load manhwas:", err);
      setError("Unable to load manhwas. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    getData();
  }, []);

  return (
    <div className="space-y-6 pb-8">
         <div className="flex w-full gap-4 p-2 pl-4 pr-4 items-center justify-center bg-zinc-900/70 backdrop-blur-lg rounded-2xl border border-zinc-800 shadow-2xl">
          <NavLink
            to="/manhwa"
            className={({ isActive }) =>
              `px-6 py-2 m-2 rounded-xl w-full text-center font-medium transition-all duration-300 ${
                isActive
                  ? 'bg-zinc-100 text-black shadow-lg scale-105'
                  : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700 hover:text-white'
              }`
            }
          >
            Manhwa
          </NavLink>

          <NavLink
            to="/jav"
            className={({ isActive }) =>
              `px-6 py-2 m-2 rounded-xl w-full text-center font-medium transition-all duration-300 ${
                isActive
                  ? 'bg-zinc-100 text-black shadow-lg scale-105'
                  : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700 hover:text-white'
              }`
            }
          >
            JAV
          </NavLink>
        </div>
      
      {/* Hero Section */}

      <div className="glassmorphism dark:glassmorphism-dark p-2 md:p-2">
        <div className="flex flex-row items-center justify-center">
          <div className="text-3xl text-nowrap pr-3 md:text-3xl font-bold mb-4 gradient-text dark:gradient-text-dark">
            Manhwa Library 
          </div>
          
          <div className="flex items-center gap-3 w-full  px-4 py-3 rounded-[24px] bg-slate-950/10 dark:bg-slate-200/10 border h-16 border-white/10">
            <input
              id="search-input"
              type="search"
              onChange={(event) => setQuery(event.target.value)}
              placeholder={"Search Items..... (ID , Actress , Tags)"}
              className="min-w-0 w-full bg-transparent outline-none text-slate-900 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500"
            />
            <button
              type="submit"
              className="inline-flex items-center justify-center rounded-2xl bg-linear-to-r from-dark-blue-600 to-purple-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-dark-blue-600/30 transition-all duration-200 hover:brightness-110"
            >
              Search
            </button>
          </div>
          <div className="pl-3 pr-3 relative">
            <button onClick={() => setShowAddInput((s) => !s)} className="inline-flex items-center justify-center rounded-2xl bg-linear-to-r from-dark-blue-700 to-purple-500 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-dark-blue-600/30 transition-all duration-200 hover:brightness-110">Add</button>

            {/* dropdown panel positioned under Add button */}
            <div
              className="absolute right-0 mt-2 w-[320px] bg-white/80 dark:bg-slate-800/90 rounded-lg p-3 shadow-lg flex items-center gap-2"
              style={{
                transformOrigin: 'top right',
                transform: showAddInput ? 'scaleY(1)' : 'scaleY(0)',
                opacity: showAddInput ? 1 : 0,
                pointerEvents: showAddInput ? 'auto' : 'none',
                transition: 'transform 160ms cubic-bezier(.2,.9,.2,1), opacity 160ms ease'
              }}
              aria-hidden={!showAddInput}
            >
              <input
                type="text"
                value={newUrl}
                onChange={(e) => setNewUrl(e.target.value)}
                placeholder="Enter URL"
                className="flex-1 rounded px-3 py-2 bg-transparent border border-white/20 text-slate-900 dark:text-slate-100"
              />
              <button
                onClick={() => {
                  console.log("Submitted URL:", newUrl);
                  scrapeManhwa(newUrl);
                  setNewUrl("");
                  setShowAddInput(false);
                }}
                className="inline-flex items-center justify-center rounded-2xl bg-linear-to-r from-dark-blue-700 to-purple-500 px-4 py-2 text-sm font-semibold text-white shadow-lg"
              >
                Submit
              </button>
            </div>
          </div>
        </div>
      </div>
      {/* Content Section  */}
      <div className="space">
                  {
                    manhwas.length > 0 ? (
                      <div className="flex justify-center flex-row flex-wrap gap-5">
                        {manhwas.map((manhwa) => (
                        <Mhw_Items manhwa={manhwa} ></Mhw_Items>
                        ))}
                      </div>
                    ) : (
                      <div>
                        <img src="https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExMnJwdzE1MWtnajdpdTA4eHNyeDFmM2RqM25jbzY1MTM0ZmJhbzczaiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/aD7el9eHQ6qjBfeFdm/giphy.gif" alt="..." srcset="" />
                      </div>
                    )
                  }
      </div>
    </div>
  );
}

export default ManhwaPage;
