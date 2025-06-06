import { createContext, useContext, useMemo } from "react";
import { CompositeProviderProps, CompositeStreamType } from "../types";
import { useCompositeStream } from "../hooks/useCompositeStream";

const CompositeContext = createContext<CompositeStreamType | undefined>(
  undefined
);

export const CompositeProvider: React.FC<CompositeProviderProps> = ({
  language,
  children,
}) => {
  const values = useCompositeStream(language);
  const memoizedValues = useMemo(() => values, [values]);
  return (
    <CompositeContext.Provider value={memoizedValues}>
      {children}
    </CompositeContext.Provider>
  );
};

export const useCompositeContext = () => {
  const context = useContext(CompositeContext);
  if (!context) {
    throw new Error(
      "useCompositeContext must be used within a CompositeProvider"
    );
  }
  return context;
};
