import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
// H.264 is the safe default for YouTube/Instagram.
Config.setCodec("h264");
