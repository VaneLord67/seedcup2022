#   Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import parl
import paddle
import numpy as np
import time

class PGAgent(parl.Agent):
    """Agent of Cartpole env.

    Args:
        algorithm(parl.Algorithm): algorithm used to solve the problem.

    """

    def __init__(self, algorithm, act_dim: int):
        super(PGAgent, self).__init__(algorithm)
        self.act_dim: int = act_dim

    def sample(self, obs) -> int:
        """Sample an action when given an observation

        Args:
            obs(np.float32): shape of (obs_dim,)
        
        Returns:
            act(int): action
        """
        sample = np.random.random()
        if sample < 0.2:
            act = np.random.randint(self.act_dim)
            return act
        
        obs = paddle.to_tensor(obs, dtype='float32')
        # fileName='log_obs.txt'
        # with open(fileName, 'a+') as file:
        #     print(f'{obs}', file=file)
        prob = self.alg.predict(obs)
        prob = prob.numpy()
        act = np.random.choice(len(prob), 1, p=prob)[0]
        return act

    def predict(self, obs):
        """Predict an action when given an observation

        Args:
            obs(np.float32): shape of (obs_dim,)
        
        Returns:
            act(int): action
        """
        obs = paddle.to_tensor(obs, dtype='float32')
        prob = self.alg.predict(obs)
        act = int(prob.argmax())
        return act

    def learn(self, obs, act, reward):
        """Update model with an episode data

        Args:
            obs(np.float32): shape of (batch_size, obs_dim)
            act(np.int32): shape of (batch_size)
            reward(np.float32): shape of (batch_size)
        
        Returns:
            loss(float)

        """
        act = np.expand_dims(act, axis=-1)
        reward = np.expand_dims(reward, axis=-1)

        obs = paddle.to_tensor(obs, dtype='float32')
        act = paddle.to_tensor(act, dtype='int32')
        reward = paddle.to_tensor(reward, dtype='float32')

        loss = self.alg.learn(obs, act, reward)
        fileName='log_loss.txt'
        with open(fileName, 'w+') as file:
            print(f"{float(loss)}", file=file)
        return float(loss)
