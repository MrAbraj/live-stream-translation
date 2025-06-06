import { useEffect, useState } from "react";
import {
  API_URL,
  defaultCompositeStreamKey,
  hindiCompositeStreamKey,
  ocrTranslatedStreamKeyHindi,
  WHEP_URL,
  WHIP_URL,
} from "../../config/config";
import { MediaMTXWebRTCReader } from "../../comon/MediaMTXWebRTCReader";
import { MediaMTXWebRTCPublisher } from "../../comon/MediaMTXWebRTCPublisher";

const displayConstraints = {
  preferCurrentTab: true,
};

export const useCompositeStream = (language: string) => {
  console.log("useCompositeStream called with language:", language);
  // Separate state for stream keys (names)
  const [webCamStreamKeys, setWebCamStreamKeys] = useState<string[]>([]);
  const [displayStreamKeys, setDisplayStreamKeys] = useState<string[]>([]);
  // Separate state for actual MediaStreams
  const [webCamStreams, setWebCamStreams] = useState<Map<string, MediaStream>>(
    new Map()
  );
  const [displayStreams, setDisplayStreams] = useState<
    Map<string, MediaStream>
  >(new Map());
  const publishStreamKey = language.includes("hindi")
    ? hindiCompositeStreamKey
    : defaultCompositeStreamKey;
  const isDefaultStream = publishStreamKey === defaultCompositeStreamKey;
  const isHindiStream = publishStreamKey === hindiCompositeStreamKey;

  // Fetch stream keys only once on mount
  useEffect(() => {
    const getAvailableStreamsFromMediaMtx = async () => {
      const response = await fetch(API_URL);
      if (!response.ok)
        throw new Error("Failed to fetch streams from MediaMTX");
      const { items } = await response.json();
      const webcamKeys = items
        .filter((item: { name: string }) => item.name.includes("webcam"))
        .map((item: { name: string }) => item.name);

      const displayKeys = items
        .filter(
          (item: { name: string }) =>
            (isDefaultStream && item.name.includes("display")) ||
            (isHindiStream && item.name.includes(ocrTranslatedStreamKeyHindi))
        )
        .map((item: { name: string }) => item.name);
      setWebCamStreamKeys(webcamKeys);
      setDisplayStreamKeys(displayKeys);
    };
    getAvailableStreamsFromMediaMtx();
  }, [isDefaultStream, isHindiStream]);

  // Only run when stream keys change
  useEffect(() => {
    const getWebrtcStream = (
      streamKeys: string[],
      streams: Map<string, MediaStream>,
      setStreams: React.Dispatch<React.SetStateAction<Map<string, MediaStream>>>
    ) => {
      streamKeys.forEach((streamKey) => {
        if (!streams.has(streamKey)) {
          const baseUrl = `${WHEP_URL}${streamKey}/`;
          new MediaMTXWebRTCReader({
            url: new URL("whep", baseUrl),
            onError: (err) => console.error("Error:", err),
            onTrack: (evt) => {
              if (evt.streams && evt.streams[0]) {
                setStreams((prev) => {
                  const updated = new Map(prev);
                  updated.set(streamKey, evt.streams[0]);
                  return updated;
                });
              }
            },
          });
        }
      });
    };
    getWebrtcStream(webCamStreamKeys, webCamStreams, setWebCamStreams);
    getWebrtcStream(displayStreamKeys, displayStreams, setDisplayStreams);
    // eslint-disable-next-line
  }, [webCamStreamKeys, displayStreamKeys]);

  const startSharingTab = async () => {
    try {
      const stream = await (navigator.mediaDevices as any).getDisplayMedia(
        displayConstraints
      );
      const baseUrl = `${WHIP_URL}${publishStreamKey}/publish`;
      new MediaMTXWebRTCPublisher({
        url:
          new URL("whip", baseUrl) +
          "?video-codec=h264%2F90000&audio-codec=pcmu%2F8000",
        stream,
        videoCodec: "h264/90000",
        videoBitrate: 10000,
        audioCodec: "pcmu/8000",
        audioBitrate: 32,
        audioVoice: true,
        onError: (err) => {
          console.error("Failed to start tab sharing:", err);
        },
        onConnected: () => {
          console.log("Tab sharing started successfully");
        },
      });
    } catch (error) {
      console.error("Error starting tab sharing:", error);
    }
  };

  return {
    webCamStreams,
    displayStreams,
    startSharingTab,
  };
};
