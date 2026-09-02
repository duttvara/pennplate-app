import { Link } from "react-router-dom";
import { Utensils } from "lucide-react";
import AuthControl from "./AuthControl";

export default function Navbar() {
  return (
    <header className="border-b border-[#6f0f2d] bg-[#8A1538] text-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
        <Link to="/" className="flex items-center gap-3 font-semibold">
          <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-md bg-white text-cranberry">
            <Utensils aria-hidden="true" size={25} strokeWidth={2.5} />
          </span>
          <span>
            <span className="block text-2xl font-black leading-none tracking-normal">PennPlate</span>
            <span className="mt-1 block max-w-[11rem] text-base font-semibold leading-5 text-white/75">
              Dining filters for campus days
            </span>
          </span>
        </Link>
        <div className="flex items-center gap-3"><span className="hidden whitespace-nowrap rounded-md border border-white/20 bg-white/10 px-4 py-3 text-lg font-medium leading-none text-white md:inline-flex">Penn Dining / Bon Appetit data</span><AuthControl /></div>
      </div>
    </header>
  );
}
