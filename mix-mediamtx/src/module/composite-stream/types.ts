export interface CompositeStreamType {
  webCamStreams: Map<string, MediaStream | undefined>;
  displayStreams: Map<string, MediaStream | undefined>;
  startSharingTab: () => Promise<void>;
}

export type CompositeProviderProps = {
  language: string;
  children: React.ReactNode;
};