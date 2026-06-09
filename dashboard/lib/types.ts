export type Platform = "youtube" | "instagram";

export type ContentStatus =
  | "idea" | "script" | "voice" | "video" | "review"
  | "approved" | "rejected" | "publishing" | "published" | "failed";

export const BOARD_COLUMNS: ContentStatus[] = [
  "idea", "script", "voice", "video", "review", "approved", "published",
];

export const STATUS_LABEL: Record<ContentStatus, string> = {
  idea: "Idee", script: "Script", voice: "Voice", video: "Video",
  review: "Klaar voor review", approved: "Goedgekeurd", rejected: "Afgekeurd",
  publishing: "Publiceren", published: "Gepubliceerd", failed: "Fout",
};

export interface Niche {
  id: string; slug: string; display_name: string; platform: Platform;
  category: string; tone: string; target_rpm_usd: number | null;
  tts_voice: string; cadence: string; is_active: boolean;
  required_disclaimers: string[]; banned_framings: string[]; topics: string[];
}

export interface Channel {
  id: string; niche_id: string; platform: Platform; handle: string;
  target_rpm_usd: number | null; is_active: boolean;
  gcp_project_id: string | null; youtube_channel_id: string | null;
  oauth_token_ref: string | null; ig_user_id: string | null;
  ig_token_ref: string | null; niches?: Niche;
}

export interface Idea {
  id: string; text: string; status: "new" | "used" | "dismissed";
  channel_id: string | null; content_id: string | null; created_at: string;
}

export interface Content {
  id: string; channel_id: string; status: ContentStatus;
  title: string | null; hook: string | null; script: string | null;
  editorial_angle: string | null; editorial_passed: boolean;
  editorial_notes: string | null; thumbnail_path: string | null;
  video_path: string | null; published_url: string | null;
  scheduled_for: string | null; updated_at: string;
  channels?: Channel;
}
