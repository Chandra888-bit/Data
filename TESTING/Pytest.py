{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "539181b7",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Define a simple function to add two numbers\n",
    "def add(a, b):\n",
    "    return a + b\n",
    "\n",
    "# Test function using pytest\n",
    "def test_add():\n",
    "    assert add(2, 3) == 5\n",
    "    assert add(-1, 1) == 0\n",
    "    assert add(0, 0) == 0"
   ]
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
