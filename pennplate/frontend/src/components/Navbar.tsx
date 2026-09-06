import { Link } from "react-router-dom";
import { Utensils } from "lucide-react";
import AuthControl from "./AuthControl";

export default function Navbar() {
  return (
    <header className="site-header">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
        <Link to="/" className="flex items-center gap-3 font-semibold">
          <span className="brand-mark flex h-11 w-11 shrink-0 items-center justify-center rounded-md">
            <Utensils aria-hidden="true" size={25} strokeWidth={2.5} />
          </span>
          <span>
            <span className="brand-name block text-2xl font-black leading-none">PennPlate</span>
            <span className="mt-1 block max-w-[11rem] text-sm font-semibold leading-4 text-ink/55">
              Dining filters for campus days
            </span>
          </span>
        </Link>
        <div className="flex items-center gap-2 sm:gap-3"><span className="source-note hidden whitespace-nowrap rounded-md px-3 py-2 text-sm font-semibold leading-none md:inline-flex">Penn Dining / Bon Appetit data</span><AuthControl /></div>
      </div>
    </header>
  );
}
