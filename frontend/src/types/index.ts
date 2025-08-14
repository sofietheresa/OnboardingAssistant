export interface Location {
  id: string;
  name: string;
  description: string;
}

export interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

export interface ChatScreenProps {
  location: Location;
  messages: Message[];
  onSendMessage: (text: string) => void;
  onBackToOnboarding: () => void;
  isLoading: boolean;
}

export interface OnboardingScreenProps {
  onChooseLocation: (id: string) => void;
}
