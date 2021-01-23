---
layout: post
title:  "Parsing Pcap with Haskell"
date:   2021-01-23 01:00:00 -0500
tags:   haskell
---

I dug up an exercise from a corner of the interet a while back, in which the prompt is to parse a sample packet capture file, filtering for specific messages and printing out some data fields. With a primary constraint that it be written in Haskell, the idea is to develop a solution that is as space and time efficient as possible. For example, although the sample file is only ~5.6MB, the program should be able to handle arbitrarily large inputs.

Some googling and using `hexdump` on the terminal breaks the Pcap global and packet headers down per [this gist](https://gist.github.com/tkuriyama/d90986828b74e8009c86ac57ad45e147), with the packet payload layout specified by the prompt.

I paired with my friend from the [Recurse Center](https://www.recurse.com/), Alex, on a few iterations. As is often the case, our list of further things to explore seems to have grown longer than the list of things we did.


**v1**

The [first, naive iteration](https://github.com/tkuriyama/puzzles/blob/master/tsuru/parser.hs) just focuses on getting the parsing and processing (printing) correct:

```haskell
main = do
  args <- getArgs
  case args of
    (fp:[]) -> decodeOrFail fp >>= printQuoteMsgs
    (fp:"-r":[]) -> (fmap reorder . decodeOrFail) fp >>= printQuoteMsgs
    ("-r":fp:[]) -> (fmap reorder . decodeOrFail) fp >>= printQuoteMsgs
    _ -> putStrLn "Args expected: filename and optional reorder flag -r"
```

The `reorder` function comes from the additional prompt that messages should be reordered by a timestamp, if so specified by a command-line flag. The prompt also notes the assumption that messages arrive no more than 3 seconds out of order. (The first version doesn't actually handle the window, so the reordering is just lifting a sort over the entire parsed input).

There seem be to a few libraries for working with binary data, but I ended up with [Data.Binary](https://hackage.haskell.org/package/binary-0.8.8.0/docs/Data-Binary.html). The main parsing logic for an individual message looks like the below. There are multiple filtering conditions for finding messages we care about, which seems to make some nesting inevitable in the `Get` monad... We experimented with `MaybeT`, but abandoned it as the additional logic slowed the execution time.

```haskell
getQuoteMsg :: Get (Maybe QuoteMsg)
getQuoteMsg = do
  (pktTime, len) <- getPacketHeader
  _ <- skip 36
  dstPort <- getInt16be
  if dstPort == 15515 || dstPort == 15516
    then do _ <- skip 4
            ids <- getByteString 5
            if ids /= B.pack [66, 54, 48, 51, 52]
              then do _ <- skip (len - 47)
                      pure Nothing
              else do (accTime, isin, bids, asks) <- getPacketData
                      pure $ Just $ QuoteMsg pktTime accTime isin bids asks
    else do _ <- skip (len - 38)
            pure $ Nothing
```


**v2**

[The second iteration](https://github.com/tkuriyama/puzzles/blob/master/tsuru/parser_v2.hs) implements the reordering logic (with 3-second window) and integrates it with priting, so that at most two passes through the input is required. This version still fully parses the input before processing, so it's constrained by available memory. 

```haskell
main :: IO ()
main = do
  args <- getArgs
  case args of
    (fp:[]) -> decodeOrFail fp >>= printQuoteMsgs
    (fp:"-r":[]) -> decodeOrFail fp >>= printReorderQuoteMsgs
    ("-r":fp:[]) -> decodeOrFail fp >>= printReorderQuoteMsgs
    _ -> putStrLn "Args expected: filename and optional reorder flag -r"
```

The reordering logic is implemented by maintaining a sorted buffer. Every time a new message is processed: (1) messages older than 3 seconds are flushed for processing (printing); and (2) the new message is inserted into the buffer, maintaining the sorted invariant.

I considered using a deque (something like `data Deque a = DQ [a] [a]`, where the first list is a "consList" holding the back of the queue normally, and the second list is a "snocList" holding the front of the queue in reverse). In theory that seems like a good idea, since old messages are flushed from the back and new messages are inserted from the front, with the practical assumption that most messages arrive reasonably ordered to start with. In practice, I couldn't find an insertion method to the snocList that would both short-circuit and indicate success (though it seems like it should be possible!). An alternative is probably to use a tree, like a BST as suggested in [this paper](http://www.eng.tau.ac.il/~nadav/pdf-files/repeated_sorting_iet_rsn.pdf).

```haskell
printReorder :: [QuoteMsg] -> [QuoteMsg] -> [QuoteMsg] -> IO ()
printReorder qs buffer flush = do
  case flush of
    [] -> case qs of
            [] -> do TIO.putStr . T.unlines . map showQuoteMsg $ buffer
                     pure ()
            _ -> do let (qs', buffer', flush') = processMsg qs buffer
                    printReorder qs' buffer' flush'
    _ -> do TIO.putStr . T.unlines . map showQuoteMsg $ flush
            printReorder qs buffer []
```


**v3**

In the [third iteration](https://github.com/tkuriyama/puzzles/blob/master/tsuru/parser_v3.hs), the code is finally refactored to a single-pass through the input, processing the messages as they are parsed. We looked at streaming libraries (mainly `streamly`), but there wasn't an obvious way to integrate with the `Data.Binary` parser without additional type conversions, so we stuck with the `runGetIncremental` pattern from `Data.Binary`.

```haskell
main :: IO ()
main = getArgs >>= \case
    (fp:[]) -> go fp processFromHandle
    (fp:"-r":[]) -> go fp processFromHandleReorder
    ("-r":fp:[]) -> go fp processFromHandleReorder
    _ -> putStrLn "Args expected: filename and optional reorder flag -r"
    where go fp = withBinaryFile fp ReadMode
```


A few runs of `time` indicate that v3 is indeed faster than v2, as expected (the reordering logic remains unchanged).

```shell
% time ./parser_v2 sample.pcap -r | tail -5
00:00:29.967475 09:00:29.94 KR4201F32820 12472@7 11104@8 9618@9 5311@10 1599@11  665@12 4965@13 3923@14 4297@15 1007@16 
00:00:29.975794 09:00:29.95 KR4301F32570 42@223 49@224 43@225 128@226 118@227  82@228 151@229 176@230 53@231 5@232 
00:00:29.974797 09:00:29.95 KR4301F32653 112@460 235@465 198@470 57@475 55@480  278@485 144@490 190@495 3@500 9@505 
00:00:29.998584 09:00:29.97 KR4301F32505 134@92 199@93 231@94 94@95 308@96  234@97 130@98 282@99 415@100 52@101 
00:00:29.996029 09:00:29.97 KR4201F32721 519@138 246@139 668@140 75@141 5@142  39@143 62@144 78@145 74@146 75@147 
./parser_v2 sample.pcap -r  3.05s user 0.08s system 98% cpu 3.166 total

% time ./parser_v3 sample.pcap -r | tail -5
00:00:29.975794 09:00:29.95 KR4301F32570 42@223 49@224 43@225 128@226 118@227  82@228 151@229 176@230 53@231 5@232 
00:00:29.974797 09:00:29.95 KR4301F32653 112@460 235@465 198@470 57@475 55@480  278@485 144@490 190@495 3@500 9@505 
00:00:29.998584 09:00:29.97 KR4301F32505 134@92 199@93 231@94 94@95 308@96  234@97 130@98 282@99 415@100 52@101 
00:00:29.996029 09:00:29.97 KR4201F32721 519@138 246@139 668@140 75@141 5@142  39@143 62@144 78@145 74@146 75@147 
processing terminated
./parser_v3 sample.pcap -r  2.20s user 0.04s system 98% cpu 2.270 total
```

**Further Iterations**

Despite the apparent simplicity of the prompt, there are quite a few interesting details to explore. Some items we haven't had a chance to try implementing yet:

- input testing -- writing an infinite stream provider, hacking larger sample files
- profiling, [criterion](https://hackage.haskell.org/package/criterion)
- experimenting with (and empirically testing) different data structures for the message buffer
- use a streaming library for practice (probably more compable and less performant? to be tested)


[GitHub code link](https://github.com/tkuriyama/puzzles/tree/master/tsuru)


