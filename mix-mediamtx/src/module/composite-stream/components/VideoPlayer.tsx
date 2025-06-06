import { Box } from "@chakra-ui/react";
import ReactPlayer from "react-player";

interface VideoPlayerProps {
  stream: MediaStream;
}

export const VideoPlayer = (props: VideoPlayerProps) => {
  const { stream } = props;
  return (
    <Box
      position="relative"
      borderRadius="16px"
      boxShadow={`
        0 0 0 2px rgba(0,255,255,0.10),   /* subtle cyan border */
        0 8px 32px 0 rgba(0,0,0,0.95),    /* deep shadow for depth */
        0 0 32px 4px rgba(0,180,255,0.22),/* blue glow for glossy look */
        0 2px 16px 0 rgba(255,255,255,0.08) /* soft white highlight */
      `}
      bg="black"
      overflow="hidden"
      transition="box-shadow 0.3s"
      borderColor="rgba(0,255,255,0.18)"
      borderWidth="1.5px"
    >
      {/* Glossy highlight at the top */}
      <Box
        position="absolute"
        top="0"
        left="0"
        right="0"
        height="18%"
        bg="linear-gradient(180deg, rgba(255,255,255,0.18) 0%, rgba(0,0,0,0) 100%)"
        borderTopRadius="16px"
        pointerEvents="none"
        zIndex={1}
      />
      <ReactPlayer
        width="100%"
        height="100%"
        url={stream}
        playing={true}
        muted={true}
        playsinline={true}
        style={{ borderRadius: 16, background: "black" }}
      />
      <style>
        {`
          .react-player__preview, .react-player__video, video {
            border-radius: 16px !important;
            background: black !important;
            overflow: hidden;
          }
        `}
      </style>
    </Box>
  );
};
