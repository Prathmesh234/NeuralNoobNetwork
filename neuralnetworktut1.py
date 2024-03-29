# -*- coding: utf-8 -*-
"""NeuralNetworkTut1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OSGkJVlTaqvHmcUemK4zr5zPinokskIR
"""



from google.colab import drive
drive.mount('/content/drive')

words = open('/names.txt', 'r').read().splitlines()

min(len(w) for w in words)

print(words[:1])

b = {}
for word in words:
  chs = ['<S>'] + list(word) + ['<E>']
  for ch1, ch2 in zip(chs, chs[1:]):
    bigram = (ch1,ch2)
    b[bigram] = b.get(bigram,0) + 1

sorted(b.items(), key = lambda kv : -kv[1] )

import torch

N = torch.zeros((27,27), dtype=torch.int32)
chars = list(sorted(set(''.join(words))))
stoi = {s:i+1 for i,s in enumerate(chars)}
stoi['.'] = 0
itos = {s:i for s,i in enumerate(chars)}
stoi

for word in words:
  chs = ['.'] + list(word) + ['.']
  for ch1, ch2 in zip(chs, chs[1:]):
    ix1 = stoi[ch1]
    ix2 = stoi[ch2]
    N[ix1, ix2]  +=1

itos

# Commented out IPython magic to ensure Python compatibility.
import matplotlib.pyplot as plt
# %matplotlib inline
plt.imshow(N)

plt.figure(figsize=(16,16))
plt.imshow(N, cmap='Blues')
for i in range(28):
  for j in range(28):
    chstr = itos[i] + itos[j]
    plt.text(j, i, chstr, ha="center", va="bottom", color="gray")
    plt.text(j, i, N[i,j].item() , ha="center", va="top", color="gray")
plt.axis('off');

N[0, :]

p = N[0].float()
p = p/p.sum()
p

g = torch.Generator().manual_seed(2147483647)
ix = torch.multinomial(p, num_samples=1, replacement=True, generator=g).item()
ix

g = torch.Generator().manual_seed(2147483647)
p = torch.rand(3, generator=g)
p = p/p.sum()
p

torch.multinomial(p, num_samples=100, replacement=True, generator=g)

P.sum(1, keepdim=True).shape

#model smoothing by adding one to prevent the inf as a lost function value
P = (N+1).float()
P /= P.sum(1, keepdim=True)

g = torch.Generator().manual_seed(2147483647)

for i in range(10):
  out = []
  ix = 0
  while True:
   p = P[ix]
   ix = torch.multinomial(p, num_samples=1, replacement=True, generator=g).item()
   out.append(itos[ix])
   if ix == 0:
     break
  print(''.join(out))

log_likelihood = 0.0
counter = 0
for word in ["pqt"]:
  chs = ['.'] + list(word) + ['.']
  for ch1, ch2 in zip(chs, chs[1:]):
    ix1 = stoi[ch1]
    ix2 = stoi[ch2]
    prob = P[ix1, ix2]
    logProb = torch.log(prob)
    log_likelihood += logProb
    counter += 1
    print(f'{ch1}{ch2}: {prob:.4f} {logProb:.4f}')


print(f'{log_likelihood=}')
#usually used by data scientist to accurately measure the lost function.
negative_log_likelihood = -log_likelihood
print(f'{negative_log_likelihood=}')
print(len(words))
#this average below will be the loss function for us in this case
print(f'{negative_log_likelihood/counter}')

#After bigram's we are going to work on neural networks
#creating the training set for the neural network from the bigram
xs, ys = [], []
for word in words[:1]:
  chs = ['.'] + list(word) + ['.']
  for ch1, ch2 in zip(chs, chs[1:]):
    ix1 = stoi[ch1]
    ix2 = stoi[ch2]
    print(ch1,ch2)
    xs.append(ix1)
    ys.append(ix2)

xs = torch.tensor(xs)
ys = torch.tensor(ys)
num = xs.nelement()

xs

ys

import torch.nn.functional as F

xenc = F.one_hot(xs, num_classes=27).float()

xenc.shape

plt.imshow(xenc)

nlls = torch.zeros(5)
for i in range(5):
  # i-th bigram:
  x = xs[i].item() # input character index
  y = ys[i].item() # label character index
  print('--------')
  print(f'bigram example {i+1}: {itos[x]}{itos[y]} (indexes {x},{y})')
  print('input to the neural net:', x)
  print('output probabilities from the neural net:', prob[i])
  print('label (actual next character):', y)
  p = prob[i, y]
  print('probability assigned by the net to the the correct character:', p.item())
  logp = torch.log(p)
  print('log likelihood:', logp.item())
  nll = -logp
  print('negative log likelihood:', nll.item())
  nlls[i] = nll

print('=========')
print('average negative log likelihood, i.e. loss =', nlls.mean().item())

#each neuron receives 27 inputs as the seed
g = torch.Generator().manual_seed(2147483647)
W = torch.randn((27,27), generator = g, requires_grad=True)
#we are doing this to regularize the W tensor
(W**2).mean()

for k in range(5):
  xenc = F.one_hot(xs, num_classes=27).float()
  logits = (xenc @ W)
  counts = logits.exp()
  prob = counts/counts.sum(1, keepdims=True)
  loss = -prob[torch.arange(num), ys].log().mean() + 0.01*(W**2).mean()
  print(loss.item())
  W.grad=None
  loss.backward()

  W.data += -0.1 * W.grad

g = torch.Generator().manual_seed(2147483647)
for k in range(5):
  out = []
  ix = 0
  while True:
    xenc = F.one_hot(torch.tensor([ix]), num_classes=27).float()
    logits = (xenc @ W)
    counts = logits.exp()
    prob = counts/counts.sum(1, keepdims=True)
    ix = torch.multinomial(prob,num_samples=1, replacement=True, generator=g).item()
    out.append(itos[ix])
    if ix == 0:
      break
  print(''.join(out))

"""
Initialization of the Random Number Generator (torch.Generator()):

g = torch.Generator().manual_seed(2147483647): This line creates a random number generator with a fixed seed (2147483647). This ensures that the random numbers generated during the execution of the code will be the same each time it is run, making the results reproducible.
Loop for Generating Sequences:

for k in range(5):: This loop iterates 5 times, each time generating a new sequence.
Initialization of Output List and Starting Index:

out = []: This creates an empty list to store the characters of the generated sequence.
ix = 0: This initializes the starting index for generating the sequence.
Sequence Generation:

while True:: This creates an infinite loop that breaks when the sequence generation is complete (when ix equals 0, indicating the end of the sequence).
xenc = F.one_hot(torch.tensor([ix]), num_classes=27).float(): This line converts the current index (ix) into a one-hot encoded vector representing the input to the neural network. The vector has a length of 27 (num_classes=27) to represent 27 different characters (including alphabets and special characters).
logits = (xenc @ W): This computes the logits (raw output) of the neural network by multiplying the one-hot encoded input vector (xenc) with the weight matrix (W).
counts = logits.exp(): This calculates the counts of each character in the output sequence by taking the exponential of the logits. This is a common technique used in language modeling to convert logits into probabilities.
prob = counts/counts.sum(1, keepdims=True): This normalizes the counts to obtain probabilities for each character. The sum(1, keepdims=True) calculates the sum of counts along the second dimension (summing the counts for each character), and keepdims=True ensures that the result retains its original shape.
ix = torch.multinomial(p,num_samples=1, replacement=True, generator=g).item(): This line samples a character index (ix) from the probability distribution p using the multinomial distribution. The num_samples=1 specifies that we want to sample only one character, replacement=True allows the same character to be sampled more than once, and generator=g specifies the random number generator to use (g).
out.append(itos[ix]): This appends the sampled character to the output list out.
if ix == 0: break: This checks if the sampled character is the end-of-sequence character (index 0) and breaks the loop if it is.

"""

#backward pass



