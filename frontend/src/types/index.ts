export interface Location {
  id: string;
  name: string;
  description: string;
}

export interface Source {
  title: string;
  doc_id: string;
  chunk_id: number;
}

export interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  fileAttachment?: FileAttachment;
  audioAttachment?: AudioAttachment;
  sources?: Source[];
}

export interface FileAttachment {
  name: string;
  size: number;
  type: string;
  url: string;
}

export interface AudioAttachment {
  duration: number;
  url: string;
}

export interface ChatScreenProps {
  location: Location;
  messages: Message[];
  onSendMessage: (
    text: string,
    fileAttachment?: FileAttachment,
    audioAttachment?: AudioAttachment,
    isUser?: boolean
  ) => void;
  onBackToOnboarding: () => void;
  isLoading: boolean;
}


export interface OnboardingScreenProps {
  onChooseLocation: (id: string) => void;
}
