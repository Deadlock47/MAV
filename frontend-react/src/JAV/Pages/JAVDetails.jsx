import React, { useEffect, useState } from "react";
import { fetchFullVideo, fetchJavDetails, fetchTrailer } from "../Helpers/Fetch";
import { useParams, useSearchParams } from "react-router-dom";
import HlsPlayer from "../../components/Video_Playr";

const fullVideoLabels = ["Mosaic", "English Dub", "Uncensored"];

const getJavseenEmbedUrl = (url) => {
  const match = url?.match(/javseen\.tv\/(\d+)/i);
  return match ? `https://javseen.tv/embed/${match[1]}/` : null;
};

const getFullVideoLabel = (url, index) => {
  const label = fullVideoLabels.find((name) =>
    url?.toLowerCase().includes(name.toLowerCase()),
  );
  return label ?? fullVideoLabels[index] ?? `Video ${index + 1}`;
};

function JAVDetails() {
  const [details, setDetails] = useState(null);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [selectedFullVideoIndex, setSelectedFullVideoIndex] = useState(0);
  const [galleryOpen, setGalleryOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [searchParams] = useSearchParams();
  const [trailers, setTrailers] = useState(null);
  const [fullVideo, setFullVideo] = useState([]);
  // const dvd_id = searchParams.get("dvd_id");
  const { dvd_id } = useParams();
  console.log(dvd_id);
  async function getData(dvd_id) {
    setLoading(true);
    try {
      const response = await fetchJavDetails(dvd_id);
      setDetails(response);
      setSelectedIndex(response?.gallery?.length > 0 ? 0 : 0);
    } catch (err) {
      console.error("Failed to load JAV Details:", err);
      // setError("Unable to load manhwas. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function getTrailer(dvd_id){
    setLoading(true);
    try {
      const response = await fetchTrailer(dvd_id);
      console.log(response);
      setTrailers(response?.trailer?.split(","));
      console.log("DFKGJDFLKJFLGKJ",trailers);
    } catch (error) {
      console.log("Error in fetching Trailer", error);
    } finally{
      setLoading(false);
    }
  }

  async function getFullVideo(dvd_id){
    setLoading(true);
     try {
      const response = await fetchFullVideo(dvd_id);
      console.log(response);
      setFullVideo(response?.fullVideo?.split(",")?? []);
      setSelectedFullVideoIndex(0);
      console.log("DFKGJDFLKJFLGKJ",fullVideo);
    } catch (error) {
      console.log("Error in fetching Trailer", error);
    } finally{
      setLoading(false);
    }
  }

  useEffect(() => {
    getData(dvd_id);
    getTrailer(dvd_id);
    getFullVideo(dvd_id);
  }, []);
  return (
    <div className="w-full h-full">
      <div
        className={`relative w-full h-[520px] -mt-10 bg-[url(${details?.jacket_full_url})] bg-cover bg-center flex items-center justify-center`}
      >
        <img
          className="relative z-30 rounded-md w-3/4 shadow-2xl"
          src={details?.jacket_full_url}
          alt=""
        />

        {/* Overlay */}
        <div className="absolute w-full inset-0 z-20 bg-gradient-to-b from-black/70 to-transparent opacity-90 flex items-end justify-center p-4">
          <p className="text-white text-center font-semibold text-sm"> </p>
        </div>
      </div>
      {/* Info */}
      <div className="relative z-30 flex w-auto -mt-48 mx-28 bg-black/10 backdrop-blur-xl border border-black/20 shadow-2xl rounded-3xl p-8 justify-center flex-row">
        <div className="w-1/5 flex justify-center">
          <img
            className=" w-4/5 rounded-2xl border border-white/10 shadow-inner"
            src={details?.jacket_thumb_url}
            alt=""
            srcset=""
          />
        </div>
        <div className="w-[1px]  bg-white">
          <br></br>
        </div>
        <div className="w-3/5  ">
          <div className="flex text-neutral-200 flex-col h-full pl-10   justify-center">
            <div className="font-bold">
              DVD ID :<span className="font-normal"> {details?.dvd_id}</span>
            </div>
            <div className="font-bold">
              Title : <span className="font-normal "> {details?.title_en}</span>
            </div>

            <div className="font-bold">
              Maker Name :{" "}
              <span className="font-normal ">
                {" "}
                {details?.maker_name_en}{" "}
              </span>{" "}
            </div>
            <div className="font-bold">
              Release Date :{" "}
              <span className="font-normal "> {details?.release_date}</span>
            </div>
            <div className="font-bold">
              Runtime :{" "}
              <span className="font-normal "> {details?.runtime_mins}</span>
            </div>
            <div className="font-bold">
              Tags :{" "}
              {details?.categories?.map((cate) => (
                <span key={cate.id} className="font-normal ">
                  {" "}
                  {cate.name_en} ,{" "}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
      {/* Image Gallery */}
      {details?.gallery?.length > 0 && (
        <div className="mx-28 mt-8 rounded-3xl bg-black/10 backdrop-blur-xl border border-black/20 p-6 shadow-2xl">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-white text-3xl font-semibold">Gallery</h2>
            <button
              type="button"
              onClick={() => setGalleryOpen(true)}
              className="rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm text-white transition hover:border-white/40 hover:bg-white/15"
            >
              Open gallery
            </button>
          </div>
          <div className="flex gap-4 overflow-x-auto pb-2">
            {details.gallery.map((item, index) => (
              <button
                key={index}
                type="button"
                onClick={() => {
                  setSelectedIndex(index);
                  setGalleryOpen(true);
                }}
                className={`flex-none overflow-hidden rounded-2xl border p-1 transition ${
                  selectedIndex === index
                    ? "border-white/80 bg-white/10"
                    : "border-white/10 bg-white/5 hover:border-white/30"
                }`}
              >
                <img
                  className="w-40 h-28 object-cover transition duration-300 group-hover:scale-105"
                  src={item.image_thumb}
                  alt={`Gallery ${index + 1}`}
                />
              </button>
            ))}
          </div>
        </div>
      )}
      {galleryOpen && details?.gallery?.length > 0 && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 px-4 py-6 backdrop-blur-sm">
          <div className="relative w-full max-w-6xl overflow-hidden rounded-3xl bg-slate-950/95 shadow-2xl">
            <button
              type="button"
              onClick={() => setGalleryOpen(false)}
              className="absolute right-4 top-4 z-40 rounded-full bg-black/60 p-3 text-white transition hover:bg-white/10"
            >
              ✕
            </button>
            <div className="relative bg-black">
              <button
                type="button"
                onClick={() =>
                  setSelectedIndex(
                    (prev) =>
                      (prev - 1 + details.gallery.length) %
                      details.gallery.length,
                  )
                }
                className="absolute left-4 top-1/2 z-40 -translate-y-1/2 rounded-full bg-black/60 p-3 text-white transition hover:bg-white/10"
              >
                ‹
              </button>
              <img
                className="w-full max-h-[80vh] object-contain"
                src={details.gallery[selectedIndex]?.image_full}
                alt={`Gallery ${selectedIndex + 1}`}
              />
              <button
                type="button"
                onClick={() =>
                  setSelectedIndex(
                    (prev) => (prev + 1) % details.gallery.length,
                  )
                }
                className="absolute right-4 top-1/2 z-40 -translate-y-1/2 rounded-full bg-black/60 p-3 text-white transition hover:bg-white/10"
              >
                ›
              </button>
            </div>
            <div className="flex gap-3 overflow-x-auto border-t border-white/10 bg-slate-950/90 p-4">
              {details.gallery.map((item, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => setSelectedIndex(index)}
                  className={`flex-none overflow-hidden rounded-2xl border p-1 transition ${
                    selectedIndex === index
                      ? "border-white/80 bg-white/10"
                      : "border-white/10 bg-white/5 hover:border-white/30"
                  }`}
                >
                  <img
                    className="h-24 w-36 object-cover"
                    src={item.image_thumb}
                    alt={`Gallery thumb ${index + 1}`}
                  />
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
      {/* Actress Details */}
      {details?.actresses?.length > 0 && (
        <div className="mx-28 mt-8 rounded-3xl bg-black/10 backdrop-blur-xl border border-black/20 p-6 shadow-2xl">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-white text-3xl font-semibold">Actress</h2>
          </div>
          <div className="flex gap-4 flex-row">
            {details.actresses.map((item, index) => (
              <div key={index} className="flex flex-col items-center">
                <img
                  className="w-50 h-50 object-cover rounded-full"
                  src={
                    "https://awsimgsrc.dmm.com/dig/mono/actjpgs/" +
                    item.image_url
                  }
                  alt={`Actress ${index + 1}`}
                />
                <p className="text-white mt-2">{item.name_romaji}</p>
              </div>
            ))}
          </div>
        </div>
      )}
      {/* Trailer  */}
      {
        <div className="mx-28 mt-8 rounded-3xl bg-black/10 backdrop-blur-xl border border-black/20 p-6 shadow-2xl">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-white text-3xl font-semibold">
              Trailer {trailers?.length}
            </h2>
          </div>
          <div className="flex gap-4 flex-row">
            <div
              key={"index"}
              className=" w-full h-full flex flex-col  items-center"
            >
              {trailers?.length && (
                //  <HlsPlayer src={`${trailers[1]}`}/>
                <video
                  src={trailers[1]}
                  controls
                  muted
                  playsInline
                  className="  object-cover rounded-xl shadow-[0px_0px_47px_14px_rgba(72,66,67,0.7)]"
                  style={{ width: "100%", maxWidth: "800px" }}
                />
              )}
            </div>
          </div>
        </div>
      }
      {/* Full Video  */}
      {fullVideo.length > 0 && (
      <div className="mx-28 mt-8 mb-20 rounded-3xl bg-black/10 backdrop-blur-xl border border-black/20 p-6 shadow-2xl">
        <div className="text-white text-3xl font-semibold">Full Video</div>
        <div className="flex p-2 justify-center w-full h-[500px]">
          <iframe
            className="w-[950px] h-full rounded-2xl shadow-[0px_0px_47px_14px_rgba(72,66,67,0.45)]"
            src={getJavseenEmbedUrl(fullVideo[selectedFullVideoIndex])}
            frameBorder="0"
            border="0"
            scrolling="no"
            width="100%"
            height="100%"
            allowFullScreen
          ></iframe>
        </div>
        <div className="mt-5 flex flex-wrap justify-center gap-3">
          {fullVideo.slice(0, 3).map((url, index) => (
            <button
              key={url}
              type="button"
              onClick={() => setSelectedFullVideoIndex(index)}
              className={`rounded-full border px-5 py-2 text-sm font-semibold transition ${
                selectedFullVideoIndex === index
                  ? "border-white/70 bg-white text-black"
                  : "border-white/20 bg-white/10 text-white hover:border-white/40 hover:bg-white/15"
              }`}
            >
              {getFullVideoLabel(url, index)}
            </button>
          ))}
        </div>
      </div>
      )}
    </div>
  );
}

export default JAVDetails;
