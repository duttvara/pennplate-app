import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import type { Session, User } from "@supabase/supabase-js";
import type { Allergen, AvoidedIngredient, FilterState, SavedPreferences } from "../types/api";
import { supabase } from "../lib/supabase";

interface AuthContextValue {
  configured: boolean;
  session: Session | null;
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<{ needsConfirmation: boolean }>;
  signOut: () => Promise<void>;
  loadPreferences: () => Promise<SavedPreferences | null>;
  savePreferences: (filters: FilterState) => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const emptyPreferences: SavedPreferences = { vegetarian: false, vegan: false, exclude: [], avoid: [] };

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(Boolean(supabase));

  useEffect(() => {
    if (!supabase) return;
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session);
      setLoading(false);
    });
    const { data: listener } = supabase.auth.onAuthStateChange((_event, nextSession) => setSession(nextSession));
    return () => listener.subscription.unsubscribe();
  }, []);

  const value = useMemo<AuthContextValue>(() => ({
    configured: Boolean(supabase),
    session,
    user: session?.user ?? null,
    loading,
    async signIn(email, password) {
      if (!supabase) throw new Error("Supabase Auth is not configured.");
      const { error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) throw error;
    },
    async signUp(email, password) {
      if (!supabase) throw new Error("Supabase Auth is not configured.");
      const { data, error } = await supabase.auth.signUp({ email, password });
      if (error) throw error;
      return { needsConfirmation: !data.session };
    },
    async signOut() {
      if (supabase) {
        const { error } = await supabase.auth.signOut();
        if (error) throw error;
      }
    },
    async loadPreferences() {
      if (!supabase || !session?.user) return null;
      const { data, error } = await supabase.from("user_preferences").select("*").eq("user_id", session.user.id).maybeSingle();
      if (error) throw error;
      if (!data) return emptyPreferences;
      return {
        vegetarian: Boolean(data.vegetarian), vegan: Boolean(data.vegan),
        exclude: (Object.entries({
          "wheat-gluten": data.avoid_wheat_gluten, milk: data.avoid_milk, egg: data.avoid_egg,
          soy: data.avoid_soy, peanut: data.avoid_peanut, "tree-nut": data.avoid_tree_nut, sesame: data.avoid_sesame
        }).filter(([, value]) => value).map(([key]) => key) as Allergen[]),
        avoid: (Object.entries({ beef: data.avoid_beef, pork: data.avoid_pork })
          .filter(([, value]) => value).map(([key]) => key) as AvoidedIngredient[])
      };
    },
    async savePreferences(filters) {
      if (!supabase || !session?.user) throw new Error("Sign in to save preferences.");
      const row = {
        user_id: session.user.id, vegetarian: filters.vegetarian, vegan: filters.vegan,
        avoid_wheat_gluten: filters.exclude.includes("wheat-gluten"), avoid_milk: filters.exclude.includes("milk"),
        avoid_egg: filters.exclude.includes("egg"), avoid_soy: filters.exclude.includes("soy"),
        avoid_peanut: filters.exclude.includes("peanut"), avoid_tree_nut: filters.exclude.includes("tree-nut"),
        avoid_sesame: filters.exclude.includes("sesame"), avoid_beef: filters.avoid.includes("beef"),
        avoid_pork: filters.avoid.includes("pork"), updated_at: new Date().toISOString()
      };
      const { error } = await supabase.from("user_preferences").upsert(row, { onConflict: "user_id" });
      if (error) throw error;
    }
  }), [loading, session]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
