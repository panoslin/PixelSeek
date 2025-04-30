/// <reference types="chrome"/>
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { VideoInfo } from '../../shared/models/video.model';

@Injectable({
  providedIn: 'root'
})
export class VideoService {
  private videosSubject = new BehaviorSubject<VideoInfo[]>([]);
  public videos$ = this.videosSubject.asObservable();

  constructor() {
    this.setupVideoListeners();
    this.loadVideos();
  }

  /**
   * Initial setup for video detection listeners
   */
  private setupVideoListeners(): void {
    // Listen for new videos from background script
    chrome.runtime.onMessage.addListener((message: any) => {
      if (message.action === 'video_detected') {
        const currentVideos = this.videosSubject.value;
        // Add new video to list if it doesn't exist
        if (!currentVideos.some(v => v.url === message.video.url)) {
          this.videosSubject.next([...currentVideos, message.video]);
        }
      }
    });
  }

  /**
   * Load all detected videos from background script
   */
  public loadVideos(): void {
    chrome.runtime.sendMessage({ action: 'get_videos' }, (response: any) => {
      if (response?.videos) {
        this.videosSubject.next(response.videos);
      }
    });
  }

  /**
   * Download a video
   */
  public downloadVideo(video: VideoInfo): Promise<boolean> {
    return new Promise((resolve, reject) => {
      chrome.runtime.sendMessage(
        { action: 'download_video', url: video.url, filename: video.filename },
        (response: any) => {
          if (response?.success) {
            resolve(true);
          } else {
            reject(response?.error || 'Download failed');
          }
        }
      );
    });
  }

  /**
   * Force check for videos on the current page
   */
  public forceCheckVideos(): Promise<void> {
    return new Promise((resolve) => {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs: chrome.tabs.Tab[]) => {
        if (tabs[0]?.id) {
          chrome.tabs.sendMessage(
            tabs[0].id,
            { action: 'force_check_videos' },
            () => {
              // Wait a bit for videos to be processed
              setTimeout(() => {
                this.loadVideos();
                resolve();
              }, 500);
            }
          );
        } else {
          resolve();
        }
      });
    });
  }
} 