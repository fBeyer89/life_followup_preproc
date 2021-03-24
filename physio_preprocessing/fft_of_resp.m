% Zeitbereich
% ----------------------------------

Fs = 0.5; %sampling frequency (1/2 Hz)
T=2; %repitition time TR=2s
L = 300; % length of signal
t = (0:L-1)*T;

load('/data/pt_life_restingstate_followup/physio/LI0026893X_resp.mat')
length(r)
plot(t,r)


Y = fft(r);
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);

f = Fs*(0:(L/2))/L;
plot(f,P1) 
title('Single-Sided Amplitude Spectrum of X(t)')
xlabel('f (Hz)')
ylabel('|P1(f)|')


%%%%%%%%%%%

Fs = 49.75; %sampling frequency (1/2 Hz)
T=0.0201; %repitition time TR=2s
L = 29851; % length of signal
t = (0:L-1)*T;

load('/data/pt_life_restingstate_followup/physio/LI0026893X.mat')

plot(t,physio.ons_secs.r)

r_long=physio.ons_secs.r;
save('/data/pt_life_restingstate_followup/physio/LI0026893X_whole_resp.mat', 'r_long', '-v7')

%physio.ons_secs.r
%Y = fft(physio.ons_secs.r);
%testvector=10 + 2*sin(0.2 * 2.0*pi*t) + 0.5*sin(0.4 * 2.0*pi*t);
testvector=10 + 2*sin(5 * 2.0*pi*t) + 0.5*sin(20 * 2.0*pi*t);

Y = fft(testvector);
P2 = abs(Y/L);
P1 = P2(1:L/2+1);
P1(2:end-1) = 2*P1(2:end-1);

f = Fs*(0:(L/2))/L;
plot(f,P1) 
title('Single-Sided Amplitude Spectrum of X(t)')
xlabel('f (Hz)')
ylabel('|P1(f)|')
