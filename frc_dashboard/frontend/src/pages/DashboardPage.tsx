import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Table,
  TableBody,
  TableRow,
  TableCell
} from '@mui/material';
import { getSystemInfo, getCalculationStats, getTeamStats } from '../services/api';
import { SystemInfo, CalculationStats } from '../types';

const DashboardPage: React.FC = () => {
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [calcStats, setCalcStats] = useState<CalculationStats | null>(null);
  const [teamStats, setTeamStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [info, calc, teams] = await Promise.all([
          getSystemInfo(),
          getCalculationStats(),
          getTeamStats()
        ]);
        setSystemInfo(info.data);
        setCalcStats(calc.data);
        setTeamStats(teams.stats);
      } catch (err: unknown) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load dashboard data';
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={3}>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Teams Loaded
              </Typography>
              <Typography variant="h4" component="div">
                {systemInfo?.teams_loaded || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={3}>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Matches
              </Typography>
              <Typography variant="h4" component="div">
                {calcStats?.total_matches_played || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={3}>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Avg Matches/Team
              </Typography>
              <Typography variant="h4" component="div">
                {calcStats?.avg_matches_per_team?.toFixed(1) || '0.0'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={3}>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Data Files
              </Typography>
              <Typography variant="h4" component="div">
                {systemInfo?.data_files || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              EPA Statistics
            </Typography>
            {calcStats && (
              <Table size="small">
                <TableBody>
                  <TableRow>
                    <TableCell>Mean</TableCell>
                    <TableCell align="right">{calcStats.epa_range.mean.toFixed(2)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Min</TableCell>
                    <TableCell align="right">{calcStats.epa_range.min.toFixed(2)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Max</TableCell>
                    <TableCell align="right">{calcStats.epa_range.max.toFixed(2)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Std Dev</TableCell>
                    <TableCell align="right">{calcStats.epa_range.std.toFixed(2)}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              OPR Statistics
            </Typography>
            {calcStats && (
              <Table size="small">
                <TableBody>
                  <TableRow>
                    <TableCell>Mean</TableCell>
                    <TableCell align="right">{calcStats.opr_range.mean.toFixed(2)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Min</TableCell>
                    <TableCell align="right">{calcStats.opr_range.min.toFixed(2)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Max</TableCell>
                    <TableCell align="right">{calcStats.opr_range.max.toFixed(2)}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Std Dev</TableCell>
                    <TableCell align="right">{calcStats.opr_range.std.toFixed(2)}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            )}
          </Paper>
        </Grid>
      </Grid>

      {teamStats && (
        <Grid container spacing={3} sx={{ mt: 3 }}>
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Top Teams
              </Typography>
              <Typography>
                Top Team: {teamStats.top_team} (EPA: {teamStats.max_epa?.toFixed(2)})
              </Typography>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Bottom Teams
              </Typography>
              <Typography>
                Bottom Team: {teamStats.bottom_team} (EPA: {teamStats.min_epa?.toFixed(2)})
              </Typography>
            </Paper>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default DashboardPage;
