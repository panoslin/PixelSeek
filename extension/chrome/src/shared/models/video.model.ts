/**
 * Model for video information
 */
export interface VideoInfo {
  url: string;
  tabId?: number;
  timestamp: number;
  type: string;
  filename: string;
  duration?: number;
  dimensions?: {
    width: number;
    height: number;
  };
} 